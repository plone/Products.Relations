import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase

import common
common.installWithinPortal()

from Products.Relations import brain
from Products.Relations import utils

class TestAdddeleteVocab(PloneTestCase.PloneTestCase):

    TYPES = 'SimpleFolder', 'SimpleType', 'ComplexType'

    def afterSetUp(self):
        # create some objects
        self.objs = common.createObjects(self, self.TYPES)
        self.brains = [brain.makeBrainAggregate(self.portal, obj.UID())
                       for obj in self.objs]

        # construct and register a ruleset
        self.ruleset = common.createRuleset(self, 'ruleset')

        # Allow self.TYPES as target
        self.ruleset.invokeFactory('Type Constraint', 'tc')
        self.ruleset.tc.setAllowedTargetTypes(self.TYPES)

    def testNoPermissions(self):
        vocab = utils.adddeleteVocab(self.objs[0])
        self.assertEquals(len(vocab), 1)
        self.assertEquals(len(vocab[0]['tuples']), 3)

        self.logout()
        vocab = utils.adddeleteVocab(self.objs[0])
        self.assertEquals(len(vocab), 0)

    def testTestOnly(self):
        vocab = utils.adddeleteVocab(self.objs[0], test_only=1)
        self.failUnless(vocab)

        self.ruleset.tc.setAllowedTargetTypes(['Gorilla'])
        vocab = utils.adddeleteVocab(self.objs[0], test_only=1)
        self.failIf(vocab)

    def testRuleSetIds(self):
        # Add another ruleset and allow all self.TYPES as targets
        self.ruleset2 = common.createRuleset(self, 'ruleset2')
        self.ruleset2.invokeFactory('Type Constraint', 'tc')
        self.ruleset2.tc.setAllowedTargetTypes(self.TYPES)

        vocab = utils.adddeleteVocab(self.objs[0])
        self.assertEquals(len(vocab), 2)
        self.failUnless(vocab[0]['id'] in ('ruleset', 'ruleset2'))
        self.failUnless(vocab[1]['id'] in ('ruleset', 'ruleset2'))

        vocab = utils.adddeleteVocab(self.objs[0], ruleset_ids=['ruleset'])
        self.assertEquals(len(vocab), 1)
        self.assertEquals(vocab[0]['id'], 'ruleset')
        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAdddeleteVocab))
    return suite

if __name__ == '__main__':
    framework()
