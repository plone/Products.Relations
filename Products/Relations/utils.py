from AccessControl import ModuleSecurityInfo
from Acquisition import aq_base
from zope.interface.declarations import Implements
from OFS.CopySupport import CopySource

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions

try:
    from Products.CMFCore.PortalFolder import PortalFolderBase
except ImportError: # catch CMF 1.4 installations here
    from Products.CMFCore.PortalFolder import PortalFolder
    PortalFolderBase = PortalFolder

from Products.Archetypes.ArchetypeTool import listTypes
from Products.Relations.brain import makeBrainAggregate
from Products.Relations.config import RELATIONS_LIBRARY
from zope import interface

modulesec = ModuleSecurityInfo('Products.Relations.utils')

class AllowedTypesByIface:
    """An approach to restrict allowed content types in a container by
    the interfaces they implement.

    Notice that extending this class means surpassing allowed_content_types,
    filter_content_types etc in the FTI, while we are still concerned about
    security."""

    # XXX: This class depends heavily on implementation details in CMF's
    #      PortalFolder. We need to eventually implement our own FTI, which
    #      should give us much cleaner code.

    allowed_interfaces = () # Don't allow anything, subclasses overwrite!

    def allowedContentTypes(self):
        """Redefines CMF PortalFolder's allowedContentTypes."""
        return self._getTIsByInterfaces(self.allowed_interfaces)

    def invokeFactory(self, type_name, id, RESPONSE = None, *args, **kwargs):
        """Invokes the portal_types tool.

        Overrides PortalFolder.invokeFactory."""
        goodType = self._portalTypeImplementsOneOfInterfaces
        if not goodType(type_name, self.allowed_interfaces):
            raise ValueError, "Type %s does not implement any of %s." % \
                  (type_name, self.allowed_interfaces)
        
        pt = getToolByName(self, 'portal_types')
        args = (type_name, self, id, RESPONSE) + args
        # XXX: PloneFolder returns an id. Do we really need to do that, too?
        new_id = pt.constructContent(*args, **kwargs)
        if not new_id: new_id = id
        return new_id

    def _verifyObjectPaste(self, object, validate_src=1):
        """Overrides PortalFolder._verifyObjectPaste."""
        # What we do here is trick PortalFolder._verifyObjectPaste in its check
        # for allowed content types. We make our typeinfo temporarily
        # unavailable.
        pt = getToolByName(self, 'portal_types')
        tmp_name = '%s_TMP' % self.portal_type
        ti = pt.getTypeInfo(self.portal_type)
        pt.manage_delObjects([self.portal_type])
        value = PortalFolderBase._verifyObjectPaste(self, object, validate_src)
        pt._setObject(self.portal_type, ti)
        return value

    def _getTIsByInterfaces(self, ifaces):
        """Returns a list of type info objects of available (AT) portal types
        implementing iface."""
        pt = getToolByName(self, 'portal_types')
        value = []
        for data in listTypes():
            klass = data['klass']
            for iface in self.allowed_interfaces:
                if iface.implementedBy(klass):
                    ti = pt.getTypeInfo(data['portal_type'])
                    if ti is not None and ti.isConstructionAllowed(self):
                        value.append(ti)
        return value

    def _portalTypeImplementsOneOfInterfaces(self, portal_type, ifaces):
        """Does the given portal_type implement one of the given interfaces?"""
        klass = self._getClassByPortalType(portal_type)
        for iface in ifaces:
            if iface.implementedBy(klass):
                return 1

    def _getClassByPortalType(self, name):
        for data in listTypes():
            if data['portal_type'] == name:
                return data['klass']
        raise ValueError, "No such portal type: %s" % name
        

def getPortalTypesByInterfaces(context, allowedIfaces):
    """Returns a list of portal type names of which the types implement any
    of the given interfaces.

    Note that allowedIfaces are strings, not Interfaces."""
    value = []
    tool = getToolByName(context, 'archetype_tool')
    for data in tool.listRegisteredTypes():
        klass = data['klass']
                   
        kifaces = [str(iface.__name__)
                   for iface in interface.implementedBy(klass).flattened()]
                   
        if [iface for iface in allowedIfaces if iface in kifaces]:
            value.append(data['portal_type'])

    return value

def getReferenceableTypes(context):
    """Return a list of portal type strings, with all types in the
    types tool that are referenceable."""
    attool = getToolByName(context, 'archetype_tool')
    pttool = getToolByName(context, 'portal_types')
    attypes = [d['portal_type'] for d in attool.listRegisteredTypes()]
    return [t for t in pttool.listContentTypes() if t in attypes]
    

modulesec.declarePublic('isReferenceable')
def isReferenceable(context):
    if getattr(aq_base(context), 'isReferenceable', None) is not None:
        return True
    else:
        return False

## TODO:
##  resolve permission discrepancies between this method and the action that calls it
##  as a condition
modulesec.declarePublic('adddeleteVocab')
def adddeleteVocab(context, test_only=0, ruleset_ids=None):
    """Make Relations vocabularies by querying all rulesets.

    What we return here is a list of dictionaries with the following
    keys:
    
      - id      the ruleset's id, which is the relationship
      - title   the ruleset's title
      - tuples  a list of tuples, see below.

    Each 'tuples' item is a 2-tuple in the form (aggregated brain,
    selected), where selected is true if there's a reference
    (source=context, target=vocab item, relationship=ruleset.id).

    If test_only=1, I will return true if *any* vocabulary item
    exists. Otherwise I will return a false value.
    """

    value = []

    membership = getToolByName(context, 'portal_membership')
    if not membership.checkPermission(permissions.ModifyPortalContent,
                                      context):
        return []

    if not isReferenceable(context):
        return []

    library = context.relations_library
    refctl = context.reference_catalog
    mtool = context.portal_membership

    if not ruleset_ids:
        rulesets = library.getRulesets()
        if None in rulesets:
            #XXX: to be fixed
            rulesets=[r for r in rulesets if r]
    else:
        rulesets = [library.getRuleset(rid) for rid in ruleset_ids]

    for ruleset in rulesets:
        if not mtool.checkPermission('View', ruleset): continue
        relationship = ruleset.getId()
        vocabulary = ruleset.makeVocabulary(context)
        if vocabulary is None: vocabulary = []
        refs = refctl(sourceUID=context.UID(), relationship=relationship)
        existing_targetUIDs = [r.targetUID for r in refs]
        if not vocabulary and not existing_targetUIDs:
            continue # we don't add an entry
        elif test_only:
            return True

        entry = {'id': relationship,
                 'title': ruleset.Title(),
                 'tuples': []}
        value.append(entry)

        tuples = entry['tuples']

        # first add all vocabulary items to 'tuples' in entry dict
        for item in vocabulary:
            selected = False
            if item.UID in existing_targetUIDs:
                selected = True
            tuples.append((item, selected))

        # now find existing refs that are not part of the vocab, which we add
        vocab_uids = [item.UID for (item, selected) in tuples]
        for uid in existing_targetUIDs:
            if uid not in vocab_uids:
                tuples.append((makeBrainAggregate(context, uid), True))

    return value

modulesec.declarePublic('getRulesetIds')        
def getRulesetIds(library, rulesetnames=[]):
    """
    Get flat list ruleset ids in named relation library subcollections
    """
    ruleset_ids = []
    if not rulesetnames:
        rulesetnames = library.objectIds()
    for name in rulesetnames:
        collection = library[name]
        ruleset_ids += [ruleset.getId() for ruleset in collection.getRulesets()]
    return ruleset_ids

modulesec.declarePublic('getRelations')        
def getRelations(context, rulesetnames=[]):
    """
    Returns all relations, filter by rulesets if needed.
    """
    result = []
    library = getToolByName(context, RELATIONS_LIBRARY)
    ruleset_ids = getRulesetIds(library, rulesetnames=rulesetnames)
    for ref in context.getReferenceImpl():
        if ref.relationship in ruleset_ids:
            ruleset = library.getRuleset(ref.relationship)
            result.append({
                'ruleset': ruleset,
                'reference': ref,
                'targetobj': ref.getTargetObject(),
                'contentobj': ref.getContentObject(),
                'actions': ruleset.listActionsFor(ref)
                })
    return result
