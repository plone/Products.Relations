import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase

from OFS.ObjectManager import BeforeDeleteException
from Products.CMFCore.utils import getToolByName

from Products.Relations.config import *
from Products.Relations import brain, exception, processor

import common
common.installWithinPortal()

class TestPortalTypeConstraint(PloneTestCase.PloneTestCase):

    TYPES = 'SimpleType', 'ComplexType'

    def afterSetUp(self):
        self.objs = common.createObjects(self, self.TYPES)
        self.brains = [brain.makeBrainAggregate(self.portal, obj.UID())
                       for obj in self.objs]

        self.ruleset = common.createRuleset(self, 'SomeRuleset')
        self.ruleset.invokeFactory('Type Constraint', 'tc')
        self.tc = getattr(self.ruleset, 'tc')

    def testMakeVocabulary(self):
        # filter
        self.tc.setAllowedTargetTypes([]) # allow any
        uc = getToolByName(self.portal, UID_CATALOG)
        brains = [brain.makeBrainAggregate(self.portal, b) for b in uc()]
        brains2 = self.tc.makeVocabulary(self.brains[0], brains)
        self.assertEquals(len(brains), len(brains2))
        
        self.tc.setAllowedTargetTypes(self.TYPES)
        self.assert_(len(brains) > 2)
        brains2 = self.tc.makeVocabulary(self.brains[0], brains)
        self.assertEquals(len(brains2), 2)

        # make list
        brains = self.tc.makeVocabulary(self.brains[0], None)
        self.assertEquals(len(brains), 2)

        # disallowed source type
        self.tc.setAllowedSourceTypes([self.TYPES[1]])
        self.assertEquals(
            self.tc.makeVocabulary(self.brains[0], None), [])

        self.tc.setAllowedTargetTypes([])
        self.assertNotEquals(self.tc.makeVocabulary(self.brains[1], None), [])

    def testValidateConnected(self):
        # triples is the arg to all calls to processConnection/Disconnection
        triples = (self.brains[0].UID, self.brains[1].UID,
                   self.ruleset.getId()),
        
        # Without setting any of allowed source or target types, connecting
        # arbitrary types is allowed:
        processor.process(self.portal, connect=triples)
        self.assertEquals(len(self.objs[0].getRefs()), 1)        
        processor.process(self.portal, disconnect=triples)
        self.assertEquals(len(self.objs[0].getRefs()), 0)

        # Source type is wrong, so we fail with a ValidationException:
        self.tc.setAllowedSourceTypes([self.TYPES[1]])
        self.assertRaises(exception.ValidationException,
                          processor.process,
                          self.portal, triples)

        # Set allowed source and target types to self.TYPES; must not raise:
        self.tc.setAllowedSourceTypes(self.TYPES)
        self.tc.setAllowedTargetTypes(self.TYPES)
        processor.process(self.portal, connect=triples)
        processor.process(self.portal, disconnect=triples)

        # Set only one target type, which is the right one:
        self.tc.setAllowedSourceTypes([])
        self.tc.setAllowedTargetTypes([self.TYPES[1]])
        processor.process(self.portal, connect=triples)
        processor.process(self.portal, disconnect=triples)
        

class TestInterfaceConstraint(PloneTestCase.PloneTestCase):

    TYPES = 'SimpleType', 'SimpleFolder'
    
    def afterSetUp(self):
        self.objs = common.createObjects(self, self.TYPES)
        self.brains = [brain.makeBrainAggregate(self.portal, obj.UID())
                       for obj in self.objs]

        self.ruleset = common.createRuleset(self, 'AnotherRuleset')
        self.ruleset.invokeFactory('Interface Constraint', 'ic')
        self.ic = getattr(self.ruleset, 'ic')

    def testMakeVocabulary(self):
        from Products.Archetypes.interfaces.base import IBaseFolder

        # filter
        self.ic.setAllowedTargetInterfaces([]) # allow any
        brains = [brain.makeBrainAggregate(self.portal, self.brains[1].UID)]
        brains2 = self.ic.makeVocabulary(self.brains[0], brains)
        self.assertEquals(len(brains), len(brains2))

        self.ic.setAllowedTargetInterfaces(['IBaseFolder'])
        brains2 = self.ic.makeVocabulary(self.brains[0], brains)
        self.assertEquals([b.UID for b in brains2], [self.brains[1].UID])
        
        # make list
        brains = self.ic.makeVocabulary(self.brains[0], None)
        for obj in [b.getObject() for b in brains]:
            self.assert_(IBaseFolder.isImplementedBy(obj))

        # disallowed source interface
        self.ic.setAllowedSourceInterfaces(['IFooBar'])
        self.assertEquals(
            self.ic.makeVocabulary(self.brains[0], None), [])

        # the first of the two allowed source interfaces is what
        # self.brains[0] implements
        self.ic.setAllowedSourceInterfaces(['IReferenceable', 'IBaseFolder'])
        brains = self.ic.makeVocabulary(self.brains[0], None)
        for obj in [b.getObject() for b in brains]:
            self.assert_(IBaseFolder.isImplementedBy(obj))

    def testValidateConnected(self):
        triples = (self.brains[0].UID, self.brains[1].UID,
                   self.ruleset.getId()),
        def connectAndDisconnect():
            processor.process(self.portal, connect=triples)
            processor.process(self.portal, disconnect=triples)

        # Without setting any of allowed source or target interfaces,
        # connecting arbitrary types is allowed:
        connectAndDisconnect()

        # Source interface is wrong, so we fail with ValidationException:
        self.ic.setAllowedSourceInterfaces(['IBaseFolder'])
        self.assertRaises(exception.ValidationException, connectAndDisconnect)

        # Set allowed interfaces to something valid; must not raise:
        self.ic.setAllowedSourceInterfaces(['IReferenceable'])
        self.ic.setAllowedTargetInterfaces(['IReferenceable'])
        connectAndDisconnect()

        # Set only target type:
        self.ic.setAllowedSourceInterfaces([])
        self.ic.setAllowedTargetInterfaces(['IBaseFolder'])
        connectAndDisconnect()


class TestCardinalityConstraint(PloneTestCase.PloneTestCase):

    TYPES = 'SimpleType', 'ComplexType', 'SimpleFolder'

    def afterSetUp(self):
        self.objs = common.createObjects(self, self.TYPES)
        self.brains = [brain.makeBrainAggregate(self.portal, obj.UID())
                       for obj in self.objs]

        self.ruleset = common.createRuleset(self, 'AThirdRuleset')
        self.ruleset.invokeFactory('Cardinality Constraint', 'cc')
        self.cc = getattr(self.ruleset, 'cc')

    def testCardinality(self):
        triples = (
            (self.brains[0].UID, self.brains[1].UID, self.ruleset.getId()),
            (self.brains[0].UID, self.brains[2].UID, self.ruleset.getId()),
            (self.brains[1].UID, self.brains[0].UID, self.ruleset.getId()),
            (self.brains[2].UID, self.brains[0].UID, self.ruleset.getId())
            )

        # no restriction:
        processor.process(self.portal, connect=triples)
        # set minimum source cardinality to 1 and try to disconnect all refs
        self.cc.setMinSourceCardinality(1)
        self.assertRaises(exception.ValidationException,
                          processor.process,
                          self.portal, (), triples)

        # set maximum source cardinality to 1 as well and disconnect one ref:
        self.cc.setMaxSourceCardinality(1)
        processor.process(self.portal, disconnect=triples[3:])

        # connect again: raises
        self.assertRaises(exception.ValidationException,
                          processor.process,
                          self.portal, triples)

        self.cc.setMinSourceCardinality(0)
        self.cc.setMaxSourceCardinality(0)

        # set minimum target cardinality to 1 and try to disconnect all refs
        self.cc.setMinTargetCardinality(1)
        self.assertRaises(exception.ValidationException,
                          processor.process,
                          self.portal, (), triples)

        # set maximum target cardinality to 1 as well and disconnect one ref:
        self.cc.setMaxTargetCardinality(1)
        processor.process(self.portal, disconnect=triples[:1])

        # connect again: raises
        self.assertRaises(exception.ValidationException,
                          processor.process,
                          self.portal, triples)

    def testCardinalityReferenceLayer(self):
        self.cc.setMinSourceCardinality(1)
        self.cc.setMinTargetCardinality(1)
        triples = (self.brains[0].UID, self.brains[1].UID,
                   self.ruleset.getId()),
        processor.process(self.portal, connect=triples)

        # now try and delete obj0:
        self.assertRaises(BeforeDeleteException, self.folder._delObject,
                          self.objs[0].id)
        self.assertEquals(self.objs[0].getRefs()[0], self.objs[1])

        # now try and delete obj1:
        self.assertRaises(BeforeDeleteException, self.folder._delObject,
                          self.objs[1].id)
        self.assertEquals(self.objs[0].getRefs()[0], self.objs[1])

        # It's ok when min = 0 and max = 1:
        self.cc.setMinSourceCardinality(0)
        self.cc.setMaxSourceCardinality(1)
        self.folder._delObject(self.objs[0].id)
        self.cc.setMinTargetCardinality(0)
        self.cc.setMaxTargetCardinality(1)
        self.folder._delObject(self.objs[1].id)


class TestInverseImplicator(PloneTestCase.PloneTestCase):

    TYPES = 'SimpleType', 'ComplexType'

    def afterSetUp(self):
        self.objs = common.createObjects(self, self.TYPES)
        self.brains = [brain.makeBrainAggregate(self.portal, obj.UID())
                       for obj in self.objs]

        self.ruleset = common.createRuleset(self, 'ARuleset')
        self.ruleset.invokeFactory('Inverse Implicator', 'ii')
        self.ii = getattr(self.ruleset, 'ii')
        self.ruleset2 = common.createRuleset(self, 'AnotherRuleset')
        self.ruleset2.invokeFactory('Inverse Implicator', 'ii')
        self.ii2 = getattr(self.ruleset2, 'ii')

    def testNoInverse(self):
        triples = (self.brains[0].UID, self.brains[1].UID,
                   self.ruleset.getId()),
        # no inverse relation is set: does not raise
        processor.process(self.portal, connect=triples)
        self.assertEquals(self.objs[0].getRefs()[0], self.objs[1])

    def testTwoInverse(self):
        self.ii.setInverseRuleset(self.ruleset2.UID())
        self.ii2.setInverseRuleset(self.ruleset.UID())

        triples = (self.brains[0].UID, self.brains[1].UID,
                   self.ruleset.getId()),
        processor.process(self.portal, connect=triples)

        self.assertEquals(
            self.objs[1].getRefs(self.ruleset2.getId())[0],
            self.objs[0])

        processor.process(self.portal, disconnect=triples)

        self.assertEquals(self.objs[0].getRefs(), [])

    def testTwoInverseDeleteOther(self):
        self.ii.setInverseRuleset(self.ruleset2.UID())
        self.ii2.setInverseRuleset(self.ruleset.UID())

        triples = (self.brains[0].UID, self.brains[1].UID,
                   self.ruleset.getId()),
        processor.process(self.portal, connect=triples)

        triples = (self.brains[1].UID, self.brains[0].UID,
                   self.ruleset2.getId()),
        processor.process(self.portal, disconnect=triples)

        self.assertEquals(self.objs[1].getRefs(), [])
        self.assertEquals(self.objs[0].getRefs(), [])

    def testInverseVocabulary(self):
        vocab = self.ii.Schema()['inverseRuleset'].Vocabulary(self.ii)
        for uid, title in vocab[:]:
            if uid:
                self.assert_(uid in (self.ruleset.UID(), self.ruleset2.UID()))

    def testProcess(self):
        self.ii.setInverseRuleset(self.ruleset2.UID())
        triples = (self.brains[0].UID, self.brains[1].UID,
                   self.ruleset.getId()),
        processor.process(self.portal, connect=triples)
        self.assertEquals(self.objs[1].getRefs()[0], self.objs[0])

        processor.process(self.portal, disconnect=triples)
        self.assertEquals(self.objs[0].getRefs(), self.objs[1].getRefs())
        self.assertEquals(self.objs[0].getRefs(), [])

####### Remove this test until we can run it conditionally
#     def testInverseWithSameTriple(self):
#         # This test requires the dpunktnpunkt-multipleref branch of
#         # Archetypes to work
#         from Products.Relations import config
#         config.ALLOW_MULTIPLE_REFS_PER_TRIPLE = True
# 
#         self.ii.setInverseRuleset(self.ruleset2.UID())
#         self.ii2.setInverseRuleset(self.ruleset.UID())
# 
#         triples = (self.brains[0].UID, self.brains[1].UID,
#                    self.ruleset.getId()),
#         processor.process(self.portal, connect=triples)
#         self.assertEquals(len(self.objs[1].getRefs()), 1)
#         self.assertEquals(self.objs[1].getRefs()[0], self.objs[0])
# 
#         ref1_uid = self.objs[1].getReferenceImpl()[0].UID()
#         processor.process(self.portal, connect=triples)
#         self.assertEquals(len(self.objs[1].getRefs()), 2)
#         refs = self.objs[1].getReferenceImpl()
#         self.failUnless(ref1_uid in [r.UID() for r in refs])
# 
#         # get the other ref's UID
#         ref2_uid = None
#         for ref in refs:
#             if ref.UID() != ref1_uid:
#                 ref2_uid = ref.UID()
#         
#         self.failIf(ref2_uid is None)

        # We can also pass reference UIDs to process disconnect:
        processor.process(self.portal, disconnect=(ref1_uid,))
        self.assertEquals(len(self.objs[1].getRefs()), 1)
        self.assertEquals(self.objs[1].getRefs()[0], self.objs[0])
        self.assertEquals(self.objs[1].getReferenceImpl()[0].UID(), ref2_uid)

        self.assertEquals(len(self.objs[0].getRefs()), 1)
        self.assertEquals(self.objs[0].getRefs()[0], self.objs[1])
        config.ALLOW_MULTIPLE_REFS_PER_TRIPLE = False

    def testInverseWithSameTripleButNotAllowed(self):
        self.ii.setInverseRuleset(self.ruleset2.UID())
        self.ii2.setInverseRuleset(self.ruleset.UID())

        triples = (self.brains[0].UID, self.brains[1].UID,
                   self.ruleset.getId()),
        processor.process(self.portal, connect=triples)
        self.assertEquals(len(self.objs[1].getRefs()), 1)
        self.assertEquals(self.objs[1].getRefs()[0], self.objs[0])

        ref1_uid = self.objs[1].getReferenceImpl()[0].UID()
        processor.process(self.portal, connect=triples)
        self.assertEquals(len(self.objs[1].getRefs()), 1)
        refs = self.objs[1].getReferenceImpl()
        self.assertNotEquals(refs[0].UID(), ref1_uid)

        self.assertEquals(len(self.objs[0].getRefs()), 1)
        self.assertEquals(self.objs[0].getRefs()[0], self.objs[1])
        self.assertEquals(self.objs[1].getRefs()[0], self.objs[0])

from Products.Relations.components import contentreference

class TestContentReferenceFinalizer(PloneTestCase.PloneTestCase):

    TYPES = 'SimpleType', 'ComplexType'

    def afterSetUp(self):
        self.objs = common.createObjects(self, self.TYPES)
        self.brains = [brain.makeBrainAggregate(self.portal, obj.UID())
                       for obj in self.objs]

        for name in ('ruleset1', 'ruleset2'):
            ruleset = common.createRuleset(self, name)
            setattr(self, name, ruleset)
            ruleset.invokeFactory('Inverse Implicator', 'ii')
            ruleset.invokeFactory('Content Reference', 'cr')

        for ruleset in self.ruleset1, self.ruleset2:
            ruleset.ii.setInverseRuleset(
                ruleset is self.ruleset1 and self.ruleset2 or self.ruleset1)
            ruleset.cr.setPortalType(self.TYPES[0])

    def reflookup(self, sUID, tUID, rel):
        rc = getToolByName(self.portal, REFERENCE_CATALOG)
        query = {'sourceUID': sUID, 'targetUID': tUID, 'relationship': rel}
        return rc(**query)[0].getObject()

    def testInverseWithSharedObject(self):
        sUID, tUID = self.brains[0].UID, self.brains[1].UID
        triples = (sUID, tUID, self.ruleset1.getId()),
        processor.process(self.portal, connect=triples)

        # Get both reference objects created
        r1 = self.reflookup(sUID, tUID, self.ruleset1.getId())
        r2 = self.reflookup(tUID, sUID, self.ruleset2.getId())

        # Make sure both are of type IContentReference
        self.assert_(contentreference.IContentReference.isImplementedBy(r1))
        self.assert_(contentreference.IContentReference.isImplementedBy(r2))

        self.assertEquals(r1.getContentObject(), r2.getContentObject())

    def testInverseWithoutSharedObject(self):
        sUID, tUID = self.brains[0].UID, self.brains[1].UID
        triples = (sUID, tUID, self.ruleset1.getId()),

        def assertDifferentObjects():
            r1 = self.reflookup(sUID, tUID, self.ruleset1.getId())
            r2 = self.reflookup(tUID, sUID, self.ruleset2.getId())

            self.assertNotEquals(r1.getContentObject(), r2.getContentObject())

        # portal types do not match
        self.ruleset2.cr.setPortalType(self.TYPES[1])
        processor.process(self.portal, connect=triples)
        assertDifferentObjects()

        # disconnect again
        processor.process(self.portal, disconnect=triples)

        # make portal types match again, this time we disable sharing
        self.ruleset2.cr.setPortalType(self.TYPES[0])
        self.ruleset2.cr.setShareWithInverse(None)
        processor.process(self.portal, connect=triples)
        assertDifferentObjects()
        
    def testSharedObjectNotCataloged(self):
        """ If shared objects are cataloged in the portal catalog, they can
            lead to problems with the Sharing UI in plone.  Adding or deleting 
            a reference can cause sharing to break with an attribute error 
            pointing to miscataloged or missing Shared Objects.
            
            This test demonstrates that Shared objects are in no longer 
            cataloged in the portal catalog.
        """
        sUID, tUID = self.brains[0].UID, self.brains[1].UID
        triples = (sUID, tUID, self.ruleset1.getId()),
        processor.process(self.portal, connect=triples)
        
        # use the sUID and the tUID to fetch the brains of the source 
        # and target objects
        pc = getToolByName(self.portal, 'portal_catalog')
        try:
            tbrains = pc(UID=tUID)[0]
        except IndexError:
            self.fail("Unable to locate the target object via UID in the portal_catalog")
        try:
            sbrains = pc(UID=sUID)[0]
        except IndexError:
            self.fail("Unable to locate the target object via UID in the portal_catalog")

        tcontents = pc(path=tbrains.getPath())
        scontents = pc(path=sbrains.getPath())
        
        self.failUnlessEqual(len(tcontents), 1, "Portal catalog shows shared object inside the target object")
        self.failUnlessEqual(len(scontents), 1, "Portal catalog shows shared object inside the source object")        

    def testReferenceActionProvider(self):
        title = 'A Title'
        self.ruleset1.cr.setTitle(title)
        # Add another CR to check if duplicates are removed in
        # Ruleset.listActionsFor
        self.ruleset1.invokeFactory('Content Reference', 'cr2')
        self.ruleset1.cr2.setPortalType(self.TYPES[0])

        triples = (self.brains[0].UID, self.brains[1].UID,
                   self.ruleset1.getId()),
        chain = processor.process(self.portal, connect=triples)
        ref = chain.added[0]
        expected = {'title': title,
                    'url': ref.getContentObject().absolute_url(),
                    'icon': ref.getContentObject().getIcon(1)}
        actions = self.ruleset1.listActionsFor(ref)
        self.assertEquals(actions[0], expected)
        self.assertEquals(len(actions), 2)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    for tc in (TestPortalTypeConstraint,
               TestInterfaceConstraint,
               TestCardinalityConstraint,
               TestInverseImplicator,
               TestContentReferenceFinalizer):
        suite.addTest(makeSuite(tc))
    return suite

if __name__ == '__main__':
    framework()
