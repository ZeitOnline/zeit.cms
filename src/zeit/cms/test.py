# Copyright (c) 2008-2009 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import unittest

from zope.testing import doctest

import zeit.cms.testing

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'content.txt'))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'async.txt',
        'cleanup.txt'))
    return suite
