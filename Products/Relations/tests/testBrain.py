import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase

from zope.interface.verify import verifyObject

import Products.Relations.interfaces as interfaces
import Products.Relations.brain as brain

import common
common.installWithinPortal()

class TestBrain(PloneTestCase.PloneTestCase):

    TYPES = 'SimpleFolder', 'SimpleType'
    
    def afterSetUp(self):
        self.objects = common.createObjects(self, self.TYPES)

    def testMakeBrainAggregate(self):
        portal = self.portal
        catalog = portal.uid_catalog

        def assertions(obj, b):
            self.assertEquals(b.getObject(), obj)
            self.assertEquals(b.UID, obj.UID())
            verifyObject(interfaces.IBrainAggregate, b)
            self.assertEquals(b.sources, ['portal_catalog'])
            self.failUnless(hasattr(b, 'EffectiveDate')) # of portal_catalog

        # three different types to use makeBrainAggregate:
        for obj in self.objects:
            # use UID
            b = brain.makeBrainAggregate(portal, obj.UID())
            assertions(obj, b)

            # use uid_catalog brain
            b = brain.makeBrainAggregate(portal, catalog(UID=obj.UID())[0])
            assertions(obj, b)

            # aggregated brain
            b = brain.makeBrainAggregate(portal, b)
            assertions(obj, b)

    def testMakeBrainAggrFromBrainCatalogsArg(self):
        portal = self.portal
        catalog = portal.uid_catalog

        b = brain.makeBrainAggrFromBrain(portal,
                                         catalog(UID=self.objects[0].UID())[0],
                                         catalogs=[])
        # assert that portal_catalog hasn't been included:
        self.assertEquals(b.sources, [])
        self.assertRaises(AttributeError, getattr, b, 'EffectiveDate')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBrain))
    return suite

if __name__ == '__main__':
    framework()
