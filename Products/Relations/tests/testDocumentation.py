import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

package = 'Products.Relations.doc'

from Products.PloneTestCase import PloneTestCase

import common
common.installWithinPortal()

class TestOverviewTxt(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.folder.invokeFactory('SimpleType', 'alfred')
        self.folder.invokeFactory('ComplexType', 'manfred')
        self.ruleset = common.createRuleset(self, 'IsParentOf')
        

def test_suite():
    from unittest import TestSuite
    from Testing.ZopeTestCase.zopedoctest import ZopeDocFileSuite

    return TestSuite((
        ZopeDocFileSuite('Overview.txt',
                         package='Products.Relations.doc',
                         test_class=TestOverviewTxt),
    ))

if __name__ == '__main__':
    framework()

