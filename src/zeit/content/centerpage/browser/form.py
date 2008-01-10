# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import datetime

import zope.formlib.form

import zeit.cms.browser.form
import zeit.cms.interfaces
import zeit.xmleditor.browser.form

import zeit.content.centerpage.interfaces


class CPFormBase(object):

    field_groups = zeit.cms.browser.form.metadataFieldGroups
    form_fields = (
        zope.formlib.form.Fields(zeit.cms.interfaces.ICMSContent) +
        zope.formlib.form.Fields(
            zeit.content.centerpage.interfaces.ICenterPageMetadata))


class AddForm(CPFormBase, zeit.cms.browser.form.AddForm):


    factory = zeit.content.centerpage.centerpage.CenterPage


class EditForm(CPFormBase, zeit.cms.browser.form.EditForm):
    """CP edit form."""


class DisplayForm(CPFormBase, zeit.cms.browser.form.DisplayForm):

    form_fields = zope.formlib.form.Fields(
        zeit.content.centerpage.interfaces.ICenterPageMetadata,
        render_context=True, omit_readonly=False)


class XMLContainerForm(zeit.xmleditor.browser.form.FormBase):

    label = 'Container bearbeiten'

    form_fields = zope.formlib.form.Fields(
        zeit.content.centerpage.interfaces.IContainer)


class XMLColumnForm(zeit.xmleditor.browser.form.FormBase):

    label = 'Column bearbeiten'

    form_fields = zope.formlib.form.Fields(
        zeit.content.centerpage.interfaces.IColumn)

