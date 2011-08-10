# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest
import zeit.cms.testing
import zope.component
import zope.security.management
import zope.testbrowser.testing


class TestTags(unittest.TestCase):

    def get_content(self):
        from zeit.cms.tagging.tag import Tags
        class Content(object):
            tags = Tags()
        return Content()

    def test_get_without_tagger_should_be_empty(self):
        self.assertEqual((), self.get_content().tags)

    def test_set_should_raise_without_tagger(self):
        def set():
            self.get_content().tags = ()
        self.assertRaises(TypeError, lambda: set())

    def test_get_should_return_tagger_values(self):
        t1 = mock.Mock()
        t2 = mock.Mock()
        t1.disabled = False
        t2.disabled = False
        with mock.patch('zeit.cms.tagging.interfaces.ITagger') as tagger:
            tagger().values.return_value = [t1, t2]
            result = self.get_content().tags
        self.assertEqual((t1, t2), result)
        tagger().values.assert_called_with()

    def test_get_should_not_return_disabled_values(self):
        t1 = mock.Mock()
        t2 = mock.Mock()
        t1.disabled = True
        t2.disabled = False
        with mock.patch('zeit.cms.tagging.interfaces.ITagger') as tagger:
            tagger().values.return_value = [t1, t2]
            result = self.get_content().tags
        self.assertEqual((t2, ), result)

    def test_set_should_enable_passed_tags(self):
        t1 = mock.Mock()
        t2 = mock.Mock()
        t1.disabled = False
        t2.disabled = False
        with mock.patch('zeit.cms.tagging.interfaces.ITagger') as tagger:
            tagger().values.return_value = [t1, t2]
            self.get_content().tags = [t1]
        self.assertFalse(t1.disabled)
        self.assertTrue(t2.disabled)
        tagger().values.assert_called_with()

    def test_set_should_set_weight_for_enabled_values(self):
        t1 = mock.Mock()
        t2 = mock.Mock()
        t1.disabled = False
        t2.disabled = False
        with mock.patch('zeit.cms.tagging.interfaces.ITagger') as tagger:
            tagger().values.return_value = [t1, t2]
            result = self.get_content().tags = [t2, t1]
        self.assertEqual(1, t1.weight)
        self.assertEqual(2, t2.weight)

    def test_set_should_set_weight_for_disabled_values_to_0(self):
        t1 = mock.Mock()
        t2 = mock.Mock()
        t1.disabled = True
        t2.disabled = True
        with mock.patch('zeit.cms.tagging.interfaces.ITagger') as tagger:
            tagger().values.return_value = [t1, t2]
            result = self.get_content().tags = []
        self.assertEqual(0, t1.weight)
        self.assertEqual(0, t2.weight)


class TestCMSContentWiring(zeit.cms.testing.FunctionalTestCase):

    # This test checks that the Tag object and its views etc are wired up
    # properly so that they can be addressed as ICMSContent and traversed to.
    # We need these things so we can use the ObjectSequenceWidget to edit tags.

    def setUp(self):
        super(TestCMSContentWiring, self).setUp()
        zope.security.management.endInteraction()
        self.browser = zope.testbrowser.testing.Browser()
        self.browser.addHeader('Authorization', 'Basic user:userpw')

    def test_object_details(self):
        from zeit.cms.tagging.tag import Tag

        whitelist = zope.component.getUtility(
            zeit.cms.tagging.interfaces.IWhitelist)
        whitelist['foo'] = Tag('foo')

        base = 'http://localhost/++skin++vivi/'
        b = self.browser
        b.open(
            base + '@@redirect_to?unique_id=tag://foo&view=@@object-details')
        self.assertEqual('<h3>foo</h3>', b.contents)