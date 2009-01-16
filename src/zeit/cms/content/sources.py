# Copyright (c) 2007-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import logging
import operator
import threading
import urllib2
import xml.sax.saxutils

import zope.component
import zope.testing.cleanup
import zope.app.appsetup.product

import zc.sourcefactory.basic
import zc.sourcefactory.contextual
import gocept.lxml.objectify
import gocept.cache.method

import zeit.cms.interfaces


logger = logging.getLogger('zeit.cms.content.sources')


class SimpleXMLSourceBase(object):

    product_configuration = 'zeit.cms'

    def _get_tree(self):
        cms_config = zope.app.appsetup.product.getProductConfiguration(
            self.product_configuration)
        url = cms_config[self.config_url]
        return self._get_tree_from_url(url)

    @gocept.cache.method.Memoize(600, ignore_self=True)
    def _get_tree_from_url(self, url):
        __traceback_info__ = (url, )
        logger.debug('Getting %s' % url)
        request = urllib2.urlopen(url)
        return gocept.lxml.objectify.fromfile(request)

    def getValues(self):
        xml = self._get_tree()
        return [unicode(serie).strip() for serie in xml.iterchildren()]


class SimpleXMLSource(
    SimpleXMLSourceBase,
    zc.sourcefactory.basic.BasicSourceFactory):
    """A simple xml source."""


class SimpleContextualXMLSource(
    SimpleXMLSourceBase,
    zc.sourcefactory.contextual.BasicContextualSourceFactory):
    """a simple contextual xml source."""

    def getValues(self, context):
        return super(SimpleContextualXMLSource, self).getValues()


class PrintRessortSource(SimpleXMLSource):

    config_url = 'source-print-ressort'


class NavigationSource(SimpleXMLSource):

    config_url = 'source-navigation'

    def getValues(self):
        tree = self._get_tree()
        return [unicode(ressort.get('name'))
                for ressort in tree.iterchildren()]

    def getTitle(self, value):
        __traceback_info__ = (value, )
        tree = self._get_tree()
        return unicode(tree.xpath('/ressorts/ressort[@name = "%s"]' %
                                  value)[0]['title'])


class SerieSource(SimpleXMLSource):

    config_url = 'source-serie'


class SubNavigationSource(SimpleContextualXMLSource):
    """Source for the subnavigation."""

    config_url = 'source-navigation'

    def getValues(self, context):
        ressort_nodes = self._get_ressort_nodes(context)
        sub_navs = reduce(
            operator.add, [ressort_node.findall('subnavigation')
             for ressort_node in ressort_nodes])
        result = set([unicode(sub.get('name'))
                    for sub in sub_navs])
        return result

    def getTitle(self, context, value):
        tree = self._get_tree()
        ressort = self._get_ressort(context)
        if ressort is None:
            nodes = tree.xpath(
                '//subnavigation[@name = %s]' % (
                    xml.sax.saxutils.quoteattr(value)))
            assert len(nodes) >= 1
        else:
            nodes = tree.xpath(
                '/ressorts/ressort[@name = %s]/subnavigation[@name = %s]' % (
                    xml.sax.saxutils.quoteattr(ressort),
                    xml.sax.saxutils.quoteattr(value)))
            assert len(nodes) == 1
        return unicode(nodes[0]['title'])

    def _get_ressort_nodes(self, context):
        tree = self._get_tree()
        all_ressorts = tree.ressort
        ressort = self._get_ressort(context)
        if not ressort:
            return all_ressorts

        nodes = tree.xpath(
            '/ressorts/ressort[@name = %s]' %
            xml.sax.saxutils.quoteattr(ressort))
        if not nodes:
            return None
        assert len(nodes) == 1
        return nodes

    def _get_ressort(self, context):
        if zeit.cms.interfaces.ICMSContent.providedBy(context):
            return None
        metadata = zeit.cms.content.interfaces.ICommonMetadata(context, None)
        if metadata is None:
            return None
        return metadata.ressort


class CMSContentTypeSource(zc.sourcefactory.basic.BasicSourceFactory):

    def getValues(self):
        return (interface for name, interface in
                zope.component.getUtilitiesFor(
                    zeit.cms.interfaces.ICMSContentType))


_collect_lock = threading.Lock()
_collect_counter = 0
@zope.component.adapter(zope.app.publication.interfaces.IBeforeTraverseEvent)
def collect_caches(event):
    """Collect method cache every 100 requests.

    Don't collect on every request because collect is O(n**2) in regard to the
    number of cached methods/functions and the amount of cached values.

    """
    global _collect_counter
    _collect_counter += 1
    locked = _collect_lock.acquire(False)
    if not locked:
        return
    try:
        if _collect_counter >= 100:
            logger.debug("Collecting caches.")
            # collect every 100 requests
            gocept.cache.method.collect()
            _collect_counter = 0
    finally:
        _collect_lock.release()


zope.testing.cleanup.addCleanUp(gocept.cache.method.clear)
