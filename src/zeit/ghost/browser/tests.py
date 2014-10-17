# Copyright (c) 2010-2011 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing
import zeit.ghost.testing


def test_suite():
    return zeit.cms.testing.FunctionalDocFileSuite(
        'checkin.txt',
        layer=zeit.ghost.testing.ZCML_LAYER,
    )
