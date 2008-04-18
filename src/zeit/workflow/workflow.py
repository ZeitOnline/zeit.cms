# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime

import pytz
import rwproperty

import zope.component
import zope.event
import zope.interface
import zope.location.location

import z3c.flashmessage.interfaces

import zeit.connector.interfaces
import zeit.cms.interfaces
import zeit.cms.content.dav
import zeit.cms.content.interfaces
import zeit.cms.checkout.interfaces
import zeit.cms.workflow.interfaces
from zeit.cms.i18n import MessageFactory as _

import zeit.workflow.interfaces


if 'all' not in globals():
    # Python 2.4 doesn't have `all` :(
    def all(iterable):
        for element in iterable:
            if not element:
                return False
        return True


WORKFLOW_NS = u'http://namespaces.zeit.de/CMS/workflow'


class LiveProperties(dict):
    """Webdav properties which are updated upon change."""

    zope.interface.implements(zeit.connector.interfaces.IWebDAVProperties)

    def __init__(self, resource):
        super(LiveProperties, self).__init__(resource.properties)
        self.resource_id = resource.id

    def __setitem__(self, key, value):
        super(LiveProperties, self).__setitem__(key, value)
        self.connector.changeProperties(self.resource_id, {key: value})

    @property
    def connector(self):
        return zope.component.getUtility(zeit.cms.interfaces.IConnector)


class Workflow(object):
    """Adapt ICMSContent to IWorkflow using the "live" data from connector.

    We must read and write properties directly from the DAV to be sure we
    actually can do the transition.
    """

    zope.interface.implements(zeit.workflow.interfaces.IWorkflow)
    zope.component.adapts(zeit.cms.interfaces.ICMSContent)

    zeit.cms.content.dav.mapProperties(
        zeit.workflow.interfaces.IWorkflow,
        WORKFLOW_NS,
        ('edited', 'corrected', 'refined', 'published',
         'images_added', 'urgent', 'date_last_published')),

    zeit.cms.content.dav.mapProperty(
        zeit.workflow.interfaces.IWorkflow['release_period'].fields[0],
        WORKFLOW_NS,
        'released_from')
    zeit.cms.content.dav.mapProperty(
        zeit.workflow.interfaces.IWorkflow['release_period'].fields[1],
        WORKFLOW_NS,
        'released_to')

    zeit.cms.content.dav.mapProperties(
        zeit.workflow.interfaces.IWorkflow,
        'http://namespaces.zeit.de/CMS/document',
        ('date_first_released', 'last_modified_by'))

    def __init__(self, context):
        self.context = context
        resource = self.connector[self.context.uniqueId]
        self.properties = LiveProperties(resource)

    @property
    def connector(self):
        return zope.component.getUtility(zeit.cms.interfaces.IConnector)

    @rwproperty.getproperty
    def release_period(self):
        return self.released_from, self.released_to

    @rwproperty.setproperty
    def release_period(self, value):
        if value is None:
            value = None, None
        self.released_from, self.released_to = value

    @property
    def date_last_modified(self):
        return zope.dublincore.interfaces.IDCTimes(self.context).modified

    def can_publish(self):
        if self.urgent:
            return True
        if all([self.edited, self.corrected, self.refined, self.images_added]):
            return True
        return False

    def publish(self):
        """Publish object."""
        if not self.can_publish():
            raise zeit.cms.workflow.interfaces.PublishingError(
                "Publish pre-conditions not satisifed.")
        zope.event.notify(
            zeit.cms.workflow.interfaces.BeforePublishEvent(self.context))
        # TODO create remotetask to actually publish. The remotetask would send
        # an IPublishedEvent then. For now set published
        self.published = True
        self.date_last_published = datetime.datetime.now(pytz.UTC)

    def retract(self):
        """Retract object."""
        # TODO create remotetask to actually retract the object.
        self.published = False


@zope.component.adapter(zeit.workflow.interfaces.IWorkflow)
@zope.interface.implementer(zeit.cms.interfaces.IWebDAVProperties)
def workflowProperties(context):
    # return properties located in the actual content object
    return zope.location.location.located(context.properties, context.context)


class FeedMetadataUpdater(object):
    """Add the expire/publication time to feed entry."""

    zope.interface.implements(
        zeit.cms.syndication.interfaces.IFeedMetadataUpdater)

    def update_entry(self, entry, content):
        workflow = zeit.workflow.interfaces.IWorkflow(content, None)
        if workflow is None:
            return

        date = ''
        if workflow.released_from:
            date = workflow.released_from.isoformat()
        entry.set('publication-date', date)

        date = ''
        if workflow.released_to:
            date = workflow.released_to.isoformat()
        entry.set('expires', date)


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.workflow.interfaces.IBeforePublishEvent)
def set_first_release_date(context, event):
    workflow = zeit.workflow.interfaces.IWorkflow(context)
    if workflow.date_first_released:
        return
    workflow.date_first_released = datetime.datetime.now(pytz.UTC)


@zope.component.adapter(
    zope.interface.Interface,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_last_modified_by(context, event):
    workflow = zeit.workflow.interfaces.IWorkflow(context, None)
    if workflow is None:
        return
    workflow.last_modified_by = event.principal.id


@zope.component.adapter(
    zeit.cms.content.interfaces.IDAVPropertiesInXML,
    zeit.cms.content.interfaces.IDAVPropertyChangedEvent)
def copy_first_released_property_to_xml(context, event):
    if ((event.property_name, event.property_namespace) !=
        ('date_first_released', WORKFLOW_NS)):
        return
    manager = zeit.cms.checkout.interfaces.ICheckoutManager(context)
    if not manager.canCheckout:
        return
    checked_out = manager.checkout()

    manager = zeit.cms.checkout.interfaces.ICheckinManager(checked_out)
    if not manager.canCheckin:
        del checked_out.__parent__[checked_out.__name__]
        return
    manager.checkin()


@zope.component.adapter(
    zope.interface.Interface,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def remove_live_properties(context, event):
    """Remove live properties from content.

    This is to make sure they don't change on checkin.

    """
    properties = zeit.connector.interfaces.IWebDAVProperties(context)
    for name, namespace in list(properties):  # make sure it's not an iterator
        if namespace == WORKFLOW_NS:
            del properties[(name, namespace)]
