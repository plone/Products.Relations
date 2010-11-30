import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import transaction

from Products.PloneTestCase import PloneTestCase
    
from OFS.SimpleItem import SimpleItem
from Products.CMFCore import interfaces as icmfcore
from Products.CMFCore.utils import getToolByName

from Products.Relations.config import *
import Products.Relations.interfaces as interfaces
import Products.Relations.brain as brain
import Products.Relations.ruleset as rulesetmodule
import Products.Relations.processor as processor

import common
common.installWithinPortal()

class TestLibrary(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.library = getToolByName(self.portal, RELATIONS_LIBRARY)

    def testRegister(self):
        ttool = getToolByName(self.portal, 'portal_types')
        construct = ttool.constructContent

        # create a ruleset in the folder given by getFolder()
        self.loginAsPortalOwner()
        self.library.getFolder().invokeFactory('Ruleset', 'ruleset1')
        self.logout(); self.login()

        # create a ruleset somewhere
        construct('Ruleset', self.folder, 'ruleset2')

        ruleset1 = getattr(self.library.getFolder(), 'ruleset1')
        ruleset2 = getattr(self.folder, 'ruleset2')
        # We don't need to register ruleset1, because it was created inside the
        # ruleset library, thus it's implicitely registered.
        self.library.registerRuleset(ruleset2)

        for ruleset in ruleset1, ruleset2:
            self.assertEquals(ruleset,
                              self.library.getRuleset(ruleset.getId()))

        self.assertEquals([ruleset1, ruleset2], self.library.getRulesets())

    def testAllowedContentTypes(self):
        # only portal owner may add rulesets
        self.loginAsPortalOwner()
        types = self.library.allowedContentTypes()
        self.assertEquals(len(types), 2)
        for t in types:
            self.assert_(str(t).endswith("Ruleset>") or
                         str(t).endswith("Ruleset Collection>"),
                         "%s not recognized" % str(t))
        self.logout()

    def testInvokeFactory(self):
        self.loginAsPortalOwner()
        lib = self.library.getFolder()
        lib.invokeFactory('Ruleset', 'allowed')
        # wrong place
        self.assertRaises(ValueError,
                          self.folder.invokeFactory,
                          'Ruleset', 'disallowed')
        # wrong type
        self.assertRaises(ValueError,
                          lib.invokeFactory,
                          'SimpleType', 'disallowed')
        self.logout()
    
    ## TODO:
    ##  rework this test to comply with current permissions settings for Products.Relations action
    def testActions(self):
        # test registration as ActionProvider and the action we define

        at = getToolByName(self.portal, 'portal_actions')

        def hasaction(obj):
            category = 'object'
            filtered_actions = at.listFilteredActionsFor(obj)
            if category not in filtered_actions.keys():
                return False
            for action in filtered_actions[category]:
                if action['id'] == 'relations':
                    return action
            return False

        ## No, that's not supposed to happen anymore
        ## all actions are registered with the actions, types, or
        ## workflow tool from CMF 2.0 onwards
        # self.assert_(RELATIONS_LIBRARY in at.listActionProviders())

        # There's no action because there's no vocabularies
        self.assert_(not hasaction(self.library))

        # We add a ruleset and a corresponding reference.
        self.loginAsPortalOwner()
        f = self.library.getFolder()
        f.invokeFactory('Ruleset', 'samerel')

        self.library.addReference(self.library, 'samerel')
        self.logout(); self.login()

        # Not there, ruleset needs to be published.
        self.assert_(not hasaction(self.library))

        self.loginAsPortalOwner()
        self.portal.portal_workflow.doActionFor(f.samerel, 'publish')
        self.logout(); self.login()

        # Still not there, we need 'Modify portal content' on the object...
        self.assert_(not hasaction(self.library))        

        # ... which we get now.
        self.loginAsPortalOwner()
        self.assert_(hasaction(self.library), "'relations' action n/a")
        self.logout(); self.login()

        # What we do here is test our action's condition in cases where context
        # is not a Referenceable.
        self.assert_(not hasaction(self.folder))

        # We create a folder which is referenceable. Inside this folder, we
        # create a document which is not.
        # We want to make sure that in the context of document we don't acquire
        # the folder's vocabulary.

        # XXX: Document is referenceable, need to find something
        # that's not referenceable.
##         self.folder.invokeFactory('SimpleFolder', 'somefolder')
##         sf = self.folder.somefolder
##         sf.invokeFactory('Document', 'somedocument')
##         sd = sf.somedocument
##         self.assertEquals(sd.UID(), sf.UID())

##         sf.addReference(sf, 'samerel')
##         action = hasaction(sf)
##         self.assert_(action)

##         self.assert_(not hasaction(sd),
##                      "%r has acquired vocabulary of %r" % (sd, sf))

    def testRenameLibrary(self):
        self.loginAsPortalOwner()
        rename = self.portal.manage_renameObject
        try:
            rename(RELATIONS_LIBRARY, 'another_id')
        except:
            pass # OK (XXX: raises CopyError currently)
        else:
            self.assert_(False,
                         "Success in renaming %s." % RELATIONS_LIBRARY)

    def testGetRulesetsOrderSupport(self):
        # Implicitly tests RulesetCollection.getRulesets
        self.loginAsPortalOwner()
        folder = self.library.getFolder()
        folder.invokeFactory('Ruleset', 'second')
        folder.invokeFactory('Ruleset', 'first')
        folder.invokeFactory('Ruleset Collection', 'collection')

        collection = folder.collection
        collection.invokeFactory('Ruleset', 'third')
        collection.invokeFactory('Ruleset Collection', 'collection')
        collection.collection.invokeFactory('Ruleset', 'fourth')

        def ids(): return [obj.getId() for obj in self.library.getRulesets()]
        
        self.assertEquals(ids(), ['second', 'first', 'third', 'fourth'])

        folder.moveObjectsToTop(['first'])
        self.assertEquals(ids(), ['first', 'second', 'third', 'fourth'])
        

# A dummy component that implements all interfaces and stores argument values
# to its methods inside self.calls, a dict that's keyed by methodnames.
class DummyComponent(SimpleItem, rulesetmodule.RuleBase):
    __implements__ = (interfaces.IVocabularyProvider,
                      interfaces.IPrimaryImplicator,
                      interfaces.IImplicator,
                      interfaces.IValidator,
                      interfaces.IFinalizer,
                      interfaces.IReferenceActionProvider,
                      interfaces.IReferenceLayerProvider,
                      interfaces.IReferenceLayer, # not a component interface
                      )

    # These methods will be generated. They don't do anything, just make
    # an entry in self.calls
    gen_methods =  ('makeVocabulary', 'isValidTarget',
                    'implyOnConnect', 'implyOnDisconnect',
                    'validateConnected', 'validateDisconnected',
                    'finalizeOnConnect', 'finalizeOnDisconnect',
                    'addHook', 'delHook')

    def __init__(self, ruleset):
        self._ruleset = ruleset
        self.calls = {}
        # We create a list for each of these methodnames, so methods
        # themselves can simply add to the list when using their name as key.
        methodnames = self.gen_methods + ('connect', 'disconnect',
                                          'provideReferenceLayer',
                                          'listActionsFor')
        for methname in methodnames:
            self.calls[methname] = []

    # We don't generate IPrimaryImplicator's 'connect' because it needs to
    # create the reference, that is, do something.
    def connect(self, source, target, metadata=None):
        self.calls['connect'].append((source, target, metadata))
        impl = rulesetmodule.DefaultPrimaryImplicator(self.getRuleset())
        return impl.connect(source, target, metadata)

    # Same with disconnect:
    def disconnect(self, reference):
        ruleset = self.getRuleset()
        self.calls['disconnect'].append((ruleset, reference))
        impl = rulesetmodule.DefaultPrimaryImplicator(ruleset)
        return impl.disconnect(reference)

    def provideReferenceLayer(self, reference):
        self.calls['provideReferenceLayer'].append((reference,))
        return self # we are our own RL

    # Don't generate, we need to return a list
    def listActionsFor(self, reference):
        self.calls['listActionsFor'].append((reference,))
        return []

def makeMethod(methname):
    def method(self, *args):
        self.calls[methname].append(args)
    return method

# Add methods to class DummyComponent
for methname in DummyComponent.gen_methods:
    setattr(DummyComponent, methname, makeMethod(methname))

class Chain(processor.Chain): # for better readability of repr
    def __repr__(self):
        l = self.added + self.deleted
        return "<Chain with %s items: %s>" % (len(l), l)

class TestRuleset(PloneTestCase.PloneTestCase):

    TYPES = 'SimpleFolder', 'SimpleType'

    def afterSetUp(self):
        # create some objects
        objs = common.createObjects(self, self.TYPES)
        self.brains = [brain.makeBrainAggregate(self.portal, obj.UID())
                       for obj in objs]

        # construct and register a ruleset
        self.ruleset = common.createRuleset(self, 'ruleset')

    def testForward(self):
        # Test if methods of Ruleset forward to component.

        # Put the dummy component inside
        component = DummyComponent(self.ruleset)
        self.ruleset._setObject('component', component)

        chain = Chain()

        # What we do now is compare the dict component.calls to what we expect
        # is called. When we compare calls['connect'] with a list containing
        # one tuple, we assert that
        #     * the method "connect" was called exactly once because the list
        #       contains one element,
        #     * the method was called with the expected arguments, namely
        #       the ones in the tuple.
        
        calls = component.calls
        self.ruleset.implyOnConnect(self.brains[0], self.brains[1], chain)
        self.assertEquals(calls['connect'],
                          [(self.brains[0], self.brains[1], None)])
        self.assertEquals(calls['implyOnConnect'],
                          [(chain.added[0], chain)])

        # provideReferenceLayer and addHook must have been called at this point
        self.assertEquals(calls['provideReferenceLayer'],
                          [(chain.added[0],)])
        self.assertEquals(calls['addHook'],
                          [(chain.added[0],)])

        # let's get the ref from the catalog and compare it to what's in added:
        ref_ctl = getToolByName(self.portal, REFERENCE_CATALOG)
        ref = ref_ctl(sourceUID=self.brains[0].UID,
                      targetUID=self.brains[1].UID,
                      relationship=self.ruleset.getId())[0].getObject()
        self.assertEquals(ref, chain.added[0])
        
        # basic assertions about the chain:
        self.assertEquals(len(chain.added), 1)
        self.assertNotEquals(chain.added[0], None)

        # makeVocabulary needs special care as well:
        self.ruleset.makeVocabulary(self.brains[0])
        self.assertEquals(calls['makeVocabulary'],
                          [(self.brains[0], None)])
        self.ruleset.makeVocabulary(self.brains[1], self.brains[:])
        self.assertEquals(calls['makeVocabulary'][1],
                          (self.brains[1], self.brains))

        # test forward to IReferenceActionProvider
        self.ruleset.listActionsFor(chain.added[0])
        self.assertEquals(calls['listActionsFor'], [(chain.added[0],)])

        # These methods all expect the same arguments,
        # namely ruleset, ref, chain:
        for method in ('validateConnected', 'validateDisconnected',
                       'finalizeOnConnect', 'finalizeOnDisconnect',
                       'implyOnDisconnect'):
            getattr(self.ruleset, method)(chain.added[0], chain)
            self.assertEquals(calls[method],
                              [(chain.added[0], chain)])

        # delHook must have been called at this point
        self.assertEquals(calls['delHook'], [(chain.added[0],)])

    def testMultipleForward(self):
        # see testForward. Adds two DummyComponents.

        component1 = DummyComponent(self.ruleset)
        component2 = DummyComponent(self.ruleset)
        self.ruleset._setObject('component1', component1)
        self.ruleset._setObject('component2', component2)

        chain = Chain()
        self.ruleset.implyOnConnect(self.brains[0], self.brains[1], chain)

        for component in component1, component2:
            # assert that first arg is ref, second arg is chain
            self.assertEquals(component.calls['implyOnConnect'],
                              [(chain.added[0], chain)])

    def testAllowedContentTypes(self):
        types = self.ruleset.allowedContentTypes()
        # We don't want to make assumptions about how many components are
        # in 'components/' and registered. We just assert that there *are*
        # components that we may add.
        self.assert_(len(types) > 0)
        for ti in types:
            self.assert_(icmfcore.ITypeInformation.providedBy(ti),
                         "%s not a type information." % ti)

    def testInvokeFactory(self):
        ti = self.ruleset.allowedContentTypes()[0]
        self.ruleset.invokeFactory(ti.id, 'allowed')
        # wrong place
        self.assertRaises(ValueError,
                          self.folder.invokeFactory,
                          ti.id, 'disallowed')
        # wrong type
        self.assertRaises(ValueError,
                          self.ruleset.invokeFactory,
                          self.TYPES[0], 'disallowed')

    def testRenameRulesetInLibrary(self):
        # tests utils.AllowedTypesByIface._verifyObjectPaste
        # and Ruleset._afterRename
        library = getToolByName(self.portal, RELATIONS_LIBRARY)
        self.loginAsPortalOwner()
        library.invokeFactory('Ruleset', 'some_id')
        ruleset = library.getRuleset('some_id')

        # Make a ref between 0 and 1 and make sure the relationship attr
        # changes according to the new name we give the ruleset.
        chain = Chain()
        ruleset.implyOnConnect(self.brains[0], self.brains[1], chain)
        ref = chain.added[-1]
        # Now rename the ruleset
        transaction.savepoint() # ensure object has a _p_jar
            
        library.manage_renameObject('some_id', 'something_else')

        # First check the attr on the ref object itself,
        self.assertEquals(ref.relationship, 'something_else')
        # then search the catalog:
        ref_ctl = getToolByName(self.portal, REFERENCE_CATALOG)
        search_kwargs = {'sourceUID': self.brains[0].UID,
                         'targetUID': self.brains[1].UID}

        search_kwargs['relationship'] = 'some_id'
        self.assertEquals(len(ref_ctl(**search_kwargs)), 0)
        search_kwargs['relationship'] = 'something_else'
        self.assertEquals(len(ref_ctl(**search_kwargs)), 1)

        # make sure our parent's type info is still there
        pt = getToolByName(self.portal, 'portal_types')
        self.assert_('Relations Library' in
                     [ti.getId() for ti in pt.listTypeInfo()])

    def testCopyRulesetInLibrary(self):
        library = getToolByName(self.portal, RELATIONS_LIBRARY)
        self.loginAsPortalOwner()        
        library.invokeFactory('Ruleset', 'some_id')
        self.assertEquals(len(library.getRefs(RELATIONSHIP_LIBRARY)), 2)

        # Now copy and make sure ruleset is registered
        cb = library.manage_copyObjects('some_id')
        library.manage_pasteObjects(cb)
        self.assertEquals(len(library.getRefs(RELATIONSHIP_LIBRARY)), 3)

    def testDefaultPrimaryImplicator(self):
        ref_ctl = getToolByName(self.portal, REFERENCE_CATALOG)

        impl = rulesetmodule.DefaultPrimaryImplicator(self.ruleset)
        
        # connect 0 and 1
        ref = impl.connect(self.brains[0], self.brains[1])
        self.assertNotEquals(ref, None)
        brains = ref_ctl(sourceUID=self.brains[0].UID,
                         targetUID=self.brains[1].UID,
                         relationship=self.ruleset.getId())
        self.assertEquals(len(brains), 1)
        self.assertEquals(ref, brains[0].getObject())

        # now do the same again, connect must returns another ref now
        ref2 = impl.connect(self.brains[0], self.brains[1])
        self.assertNotEquals(ref2, None)

        # Only one reference lives in the catalog, the other one was
        # 'updated'
        brains = ref_ctl(sourceUID=self.brains[0].UID,
                         targetUID=self.brains[1].UID,
                         relationship=self.ruleset.getId())
        self.assertEquals(len(brains), 1)

####### Remove this test until we can run it conditionally
#     def testDefaultPrimaryImplicatorMultipleRefsPerTriple(self):
#         # This test requires the dpunktnpunkt-multipleref branch of
#         # Archetypes to work
#         from Products.Relations import config
#         config.ALLOW_MULTIPLE_REFS_PER_TRIPLE = True
# 
#         ref_ctl = getToolByName(self.portal, REFERENCE_CATALOG)
# 
#         impl = rulesetmodule.DefaultPrimaryImplicator(self.ruleset)
#         
#         # connect 0 and 1
#         ref = impl.connect(self.brains[0], self.brains[1])
#         self.assertNotEquals(ref, None)
#         brains = ref_ctl(sourceUID=self.brains[0].UID,
#                          targetUID=self.brains[1].UID,
#                          relationship=self.ruleset.getId())
#         self.assertEquals(len(brains), 1)
#         self.assertEquals(ref, brains[0].getObject())
# 
#         # now do the same again, connect must returns another ref now
#         ref2 = impl.connect(self.brains[0], self.brains[1])
#         self.assertNotEquals(ref2, None)
# 
#         # Now two references with the sample source, target and
#         # relationship live in the catalog
#         brains = ref_ctl(sourceUID=self.brains[0].UID,
#                          targetUID=self.brains[1].UID,
#                          relationship=self.ruleset.getId())
#         self.assertEquals(len(brains), 2)
#         ref_uids = [b.UID for b in brains]
#         self.failUnless(ref.UID() in ref_uids)
#         self.failUnless(ref2.UID() in ref_uids)
#         
#         config.ALLOW_MULTIPLE_REFS_PER_TRIPLE = False        

    def testReferenceWithBrains(self):
        # tests class ReferenceWithBrains of module brain (XXX)
        chain = Chain()
        self.ruleset.implyOnConnect(self.brains[0], self.brains[1], chain)
        ref = self.brains[0].getObject().getReferenceImpl()[0]
        self.assertEquals(ref.getSourceBrain(), self.brains[0])
        self.assertEquals(ref.getTargetBrain(), self.brains[1])
        self.assertEquals(ref.getSourceObject(), self.brains[0].getObject())
        self.assertEquals(ref.getTargetObject(), self.brains[1].getObject())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    tests = TestLibrary, TestRuleset
    for test in tests:
        suite.addTest(makeSuite(test))
    return suite

if __name__ == '__main__':
    framework()
