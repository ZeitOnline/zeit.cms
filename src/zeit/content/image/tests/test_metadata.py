# Copyright (c) 2013 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.content.interfaces import IXMLReference
from zeit.cms.interfaces import ICMSContent
from zeit.content.image.interfaces import IImageMetadata
import lxml.etree
import zeit.cms.testing
import zeit.content.image.testing
import zope.component


class ImageMetadataTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.image.testing.ZCML_LAYER

    def test_nofollow_is_written_to_rel_attribute(self):
        image = ICMSContent('http://xml.zeit.de/2006/DSC00109_2.JPG')
        with zeit.cms.checkout.helper.checked_out(image) as co:
            metadata = IImageMetadata(co)
            metadata.copyrights = (('Foo', 'http://example.com', True),)
        ref = zope.component.getAdapter(image, IXMLReference, name='image')
        self.assertEllipsis("""\
<image...>
  ...
  <copyright py:pytype="str" link="http://example.com" rel="nofollow">Foo</copyright>
</image>
""", lxml.etree.tostring(ref, pretty_print=True))