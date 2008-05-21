import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase

import common
common.installWithinPortal()

class TestSomething(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        pass

##     def testSomething(self):
##         self.assertEqual(2, 1+1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSomething))
    return suite

if __name__ == '__main__':
    framework()
