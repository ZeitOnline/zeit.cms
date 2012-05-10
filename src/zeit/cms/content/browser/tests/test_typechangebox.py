# coding: utf8
# Copyright (c) 2009-2012 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.testing


class TestTypeChangeBox(zeit.cms.testing.SeleniumTestCase):

    def test_box_should_scroll(self):
        s = self.selenium
        self.open('/repository/online/2007/01/Somalia')
        s.selenium.set_window_size(1000, 300)
        s.waitForEval('window.outerHeight', '300')
        s.click('xpath=//a[@title="Additional actions"]')
        s.click('link=Change type')
        s.waitForElementPresent('css=.lightbox-full')
        scroll = s.getAttribute('css=.lightbox-full@scrollHeight')
        offset = s.getAttribute('css=.lightbox-full@offsetHeight')
        self.assertGreater(scroll, offset)
