# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import zope.app.component.hooks
import zope.app.component
import zope.app.zopeappgenerations

import zc.notification.interfaces

import zeit.cms.content.interfaces
import zeit.cms.content.template
import zeit.cms.notification.utility
import zeit.cms.repository.interfaces
import zeit.cms.repository.repository
import zeit.cms.workingcopy.workingcopy


def installLocalUtility(root, factory, name, interface, utility_name=u''):
    utility = factory()
    root[name] = utility
    site_manager = zope.component.getSiteManager()
    site_manager.registerUtility(utility, interface, name=utility_name)
    return root[name]


def install(root):
    site_manager = zope.component.getSiteManager()
    installLocalUtility(
        root, zeit.cms.repository.repository.repositoryFactory,
        'repository', zeit.cms.repository.interfaces.IRepository)
    installLocalUtility(
        root, zeit.cms.workingcopy.workingcopy.WorkingcopyLocation,
        'workingcopy', zeit.cms.workingcopy.interfaces.IWorkingcopyLocation)
    installLocalUtility(
        root, zeit.cms.content.template.TemplateManagerContainer,
        'templates', zeit.cms.content.interfaces.ITemplateManagerContainer)
    installLocalUtility(
        site_manager, zeit.cms.notification.utility.notificationUtilityFactory,
        'notification', zc.notification.interfaces.INotificationUtility)


def evolve(context):
    site = zope.app.component.hooks.getSite()
    try:
        root = zope.app.zopeappgenerations.getRootFolder(context)
        zope.app.component.hooks.setSite(root)
        install(root)
    finally:
        zope.app.component.hooks.setSite(site)
