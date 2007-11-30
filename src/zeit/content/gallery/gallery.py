# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import xml.sax.saxutils
import StringIO

import lxml.etree
import lxml.objectify
import gocept.lxml.interfaces
import gocept.lxml.objectify
import rwproperty

import persistent

import zope.component
import zope.interface
import zope.lifecycleevent
import zope.location.location

import zope.app.container.contained

import zeit.cms.connector
import zeit.cms.interfaces
import zeit.cms.content.metadata
import zeit.cms.content.util
import zeit.content.gallery.interfaces


# A gallery used to be a center page, that's why we initialize it with such a
# template.
GALLERY_TEMPLATE = u"""\
<centerpage>
    <head/>
    <body>
        <column layout="left"/>
        <column layout="right">
            <container/>
        </column>
    </body>
</centerpage>"""



class Gallery(persistent.Persistent,
              zope.app.container.contained.Contained,
              zeit.cms.content.metadata.CommonMetadata):
    """CenterPage"""

    zope.interface.implements(zeit.content.gallery.interfaces.IGallery)

    _image_folder = zeit.cms.content.property.SingleResourceProperty(
        '.head.image-folder')

    uniqueId = None
    __name__ = None

    def __init__(self, xml_source=None):
        if xml_source is None:
            xml_source = StringIO.StringIO(GALLERY_TEMPLATE)
        self.xml = gocept.lxml.objectify.fromfile(xml_source)

    @property
    def xml_source(self):
        return lxml.etree.tostring(self.xml, 'UTF-8', xml_declaration=True)

    @rwproperty.getproperty
    def image_folder(self):
        return self._image_folder

    @rwproperty.setproperty
    def image_folder(self, image_folder):
        self._image_folder = image_folder
        self.reload_image_folder()

    def reload_image_folder(self):
        image_folder = self.image_folder
        for name in image_folder:
            image = image_folder[name]
            entry = zeit.content.gallery.interfaces.IGalleryEntry(image, None)
            if entry is None:
                if name in self:
                    # Ignore all non image types
                    del self[name]
            else:
                if name not in self:
                    self[name] = entry

    # container interface

    def __getitem__(self, key):
        """Get a value for a key

        A KeyError is raised if there is no value for the key.
        """
        node = self._get_block_for_key(key)
        if node is None:
            raise KeyError(key)
        image_name = node.get('name')
        # XXX what happens if the image goes away?
        image = self.image_folder[image_name]
        entry = zeit.content.gallery.interfaces.IGalleryEntry(image)
        entry.title = node.get('title')
        if entry.title is not None:
            entry.title = unicode(entry.title)
        entry.text = unicode(node['text'])
        return zope.location.location.located(entry, self, key)

    def get(key, default=None):
        """Get a value for a key

        The default is returned if there is no value for the key.
        """

    def __contains__(self, key):
        """Tell if a key exists in the mapping."""
        return self._get_block_for_key(key) is not None

    def keys(self):
        """Return the keys of the mapping object.
        """
        return (unicode(name)
                for name in self._entries_container.xpath('block/@name'))

    def __iter__():
        """Return an iterator for the keys of the mapping object.
        """

    def values():
        """Return the values of the mapping object.
        """

    def items():
        """Return the items of the mapping object.
        """

    def __len__(self):
        return self._entries_container.xpath('count(block)')

    def __setitem__(self, key, value):
        node = gocept.lxml.interfaces.IObjectified(value)
        node.set('name', key)

        old_node = self._get_block_for_key(key)
        if old_node is None:
            self._entries_container.append(node)
        else:
            old_node.getparent().replace(old_node, node)

        self._p_changed = True

    @property
    def _entries_container(self):
        return self.xml['body']['column'][1]['container']

    def _get_block_for_key(self, key):
        matching_blocks = self._entries_container.xpath(
            'block[@name=%s]' % xml.sax.saxutils.quoteattr(key))
        if matching_blocks:
            assert len(matching_blocks) == 1
            return matching_blocks[0]


@zope.interface.implementer(zeit.content.gallery.interfaces.IGallery)
@zope.component.adapter(zeit.cms.interfaces.IResource)
def galleryFactory(context):
    obj = Gallery(xml_source=context.data)
    zeit.cms.interfaces.IWebDAVProperties(obj).update(context.properties)
    return obj


resourceFactory = zeit.cms.connector.xmlContentToResourceAdapterFactory(
    'image-gallery')
resourceFactory = zope.component.adapter(
    zeit.content.gallery.interfaces.IGallery)(resourceFactory)


@zope.component.adapter(
    zeit.content.gallery.interfaces.IGallery,
    zeit.cms.content.interfaces.IDAVPropertyChangedEvent)
def mapPropertyToAttribute(cp, event):
    attribute = zeit.cms.content.property.AttributeProperty(
        event.property_namespace, event.property_name)
    attribute.__set__(cp, event.new_value)


@zope.component.adapter(zeit.content.image.interfaces.IImage)
@zope.interface.implementer(zeit.content.gallery.interfaces.IGalleryEntry)
def galleryentry_factory(context):
    entry = GalleryEntry()
    entry.image = context
    entry.thumbnail = None  # XXX
    entry.title = None
    entry.text = u''
    return entry


class GalleryEntry(object):

    zope.interface.implements(zeit.content.gallery.interfaces.IGalleryEntry)


@zope.component.adapter(zeit.content.gallery.interfaces.IGalleryEntry)
@zope.interface.implementer(gocept.lxml.interfaces.IObjectified)
def objectified_entry(context):
        node = lxml.objectify.XML('<block/>')
        if context.title:
            node['title'] = context.title
        node['text'] = context.text
        node['image'] = gocept.lxml.interfaces.IObjectified(
            context.image)
        return node


@zope.component.adapter(
    zeit.content.gallery.interfaces.IGalleryEntry,
    zope.lifecycleevent.IObjectModifiedEvent)
def update_gallery_on_entry_change(entry, event):
    entry.__parent__[entry.__name__] = entry
