# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import logging
import lxml.etree
import zope.component
import zope.interface

import zeit.cms.interfaces
import zeit.cms.checkout.interfaces
import zeit.cms.checkout.helper
import zeit.cms.content.interfaces
import zeit.cms.related.interfaces
import zeit.cms.relation.interfaces


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IBeforeCheckinEvent)
def update_index_on_checkin(context, event):
    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    relations.index(context)

def update_relating_of_checked_out(checked_out):
    """Update the objects which relate the checked_out."""
    related = zeit.cms.related.interfaces.IRelatedContent(
        checked_out, None)
    if related is None:
        return False

    # Get an xml representation of the related to check if anything was
    # actually changed
    xml_before = lxml.etree.tostring(
        zeit.cms.content.interfaces.IXMLRepresentation(related).xml)

    # Update related
    related.related = related.related

    # Make sure there actually was a change.
    xml_after = lxml.etree.tostring(
        zeit.cms.content.interfaces.IXMLRepresentation(related).xml)

    if xml_before == xml_after:
        return False

    # Okay to be really sure this isn't just some xml snafu put both xmls
    # through an etree again
    if (lxml.etree.tostring(lxml.etree.fromstring(xml_before)) ==
        lxml.etree.tostring(lxml.etree.fromstring(xml_after))):
        return False

    return True


@zope.component.adapter(
    zeit.cms.interfaces.ICMSContent,
    zeit.cms.checkout.interfaces.IAfterCheckinEvent)
def update_relating(context, event):
    """Update metadata in object which relates another."""
    relations = zope.component.getUtility(
        zeit.cms.relation.interfaces.IRelations)
    relating_objects = relations.get_relations(context, 'related')
    for related_object in relating_objects:
        zeit.cms.checkout.helper.with_checked_out(
            related_object, update_relating_of_checked_out)
