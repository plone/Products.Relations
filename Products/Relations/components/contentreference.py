from Globals import InitializeClass
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
try: # New CMF  
    from Products.CMFCore import permissions as CMFCorePermissions 
except: # Old CMF  
    from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.PortalFolder import PortalFolderBase
from Products.Archetypes.public import *
from Products.Archetypes.utils import shasattr
from Products.Archetypes.ReferenceEngine import Reference
from Products.Archetypes.interfaces.referenceengine \
     import IContentReference as IATContentReference
from Products.Archetypes.interfaces import IReference

# Maybe some day we will get consistency on how implements works
# so that we don't have to do this - cwarner
from zope.interface import implements
from zope.interface import classImplements
from Products.Archetypes.interfaces import IBaseContent
from Products.Archetypes.interfaces import IReferenceable
from Products.Archetypes.interfaces import IExtensibleMetadata

from Products.Archetypes.utils import getRelPath, getRelURL

from Products.Relations.config import *
from Products.Relations import interfaces, ruleset, utils
from Products.Relations.schema import BaseSchemaWithInvisibleId
import inverse

def inf_range():
    i = 0
    while 1:
        yield str(i)
        i = i + 1

class IContentReference(IATContentReference):
    def getContentObjects(self):
        """Returns the content objects associated with this reference."""

class ContentReference(ruleset.RLMWithBrains, PortalFolderBase):
    """Resembles Archetypes.ReferenceEngine.ContentReference.

    Note that portal objects associated with this reference are identified
    by a reference, not by containment."""
    
    portal_type = meta_type = "Relation ContentReference"
    
    def getContentObject(self):
        objs = self.getRefs(RELATIONSHIP_CONTENTREF)
        if len(objs): return objs[0] # this means ignoring the rest
        else: return None

    def getContentObjects(self):
        return self.getRefs(RELATIONSHIP_CONTENTREF)
    
    def _catalogRefs(self, aq, uc=None, rc=None):
        ruleset.RLMWithBrains._catalogRefs(self,aq,uc,rc)
        
        # Use the PortalFolderBase implementation to avoid the false
        # result from a bogus inheritence of SimpleItem
        names = PortalFolderBase.objectIds(self)
        
        for name in names:
            if not shasattr(self, name):
                break

            obj=getattr(self,name)
            if obj:
                #import pdb;pdb.set_trace()
                if not uc:
                    uc = getToolByName(aq, config.UID_CATALOG)
                if not rc:
                    rc = getToolByName(aq, config.REFERENCE_CATALOG)
    
                url = getRelURL(uc, obj.getPhysicalPath())
                uc.catalog_object(obj, url)
                #rc.catalog_object(obj, url)
                
                obj._catalogRefs(uc, uc, rc)



InitializeClass(ContentReference)

try:
    classImplements(ContentReference, IContentReference)    
except TypeError:
    ContentReference.__implements__ = (IContentReference)


def _makeKey(relationship, sUID, tUID, portal_type):
    return "relationship: %s\n" % relationship + \
           "source: %s\n" % sUID + \
           "target: %s\n" % tUID + \
           "type of shared object: %s\n" % portal_type

def _findInstanceOf(l, klass):
    for obj in l:
        if isinstance(obj, klass):
            return obj

class ContentReferenceFinalizer(BaseContent, ruleset.RuleBase):
    """PrimaryImplicator and Finalizer that associates a portal object
    with a reference.

    I am aware of InverseImplicator and I allow a reference and its
    inverse to share one portal object.

    References that I create conform to this module's
    IContentReference, which derives from
    Archetypes.interfaces.referenceengine.IContentReference."""
    implements(interfaces.IPrimaryImplicator, interfaces.IFinalizer, interfaces.IReferenceActionProvider,
               IBaseContent, IReferenceable, IExtensibleMetadata)

    def connect(self, source, target, metadata=None):
        impl = ruleset.DefaultPrimaryImplicator(self.getRuleset())
        impl.referenceClass = ContentReference
        return impl.connect(source, target, metadata)

    def disconnect(self, reference):
        impl = ruleset.DefaultPrimaryImplicator(self.getRuleset())
        return impl.disconnect(reference)

    def finalizeOnConnect(self, reference, chain):
        # XXX: Implementation needs to be redone
        if not self.getPortalType():
            raise ValueError,"%s has no portal type set." % self.absolute_url()

        obj = self._lookForSharedObject(reference, chain)
        if obj is None:
            # if there's no shared object, we need to create it and put it
            # inside the chain, so that others can share with us
            tt = getToolByName(self, 'portal_types')

            # XXX: I dunno why reference.object_ids() always returns ().
            for name in inf_range():
                if not shasattr(reference, name):
                    break
            
            tt.constructContent(
                self.getPortalType(), # contentType
                reference, # container
                name # id
                )

            obj = getattr(reference, name)
            
            # uncatalog the newly created object from the portal catalog
            # it doesn't need to be there, and causes problems when it is.
            obj.unindexObject()
            
            obj.setTitle(self.Title())
            if self.getShareWithInverse():
                key = _makeKey(self.getRuleset().getId(),
                               reference.sourceUID, reference.targetUID,
                               self.getPortalType())
                chain[self.__class__.__name__][key] = obj
        
        # unfortunally this is needed for RelationsIndex unindex. The archetypes
        # crap implementation uses manage_beforeDelete and this is called before
        # ObjectWillBeRemovedEvent is notified. So we dont have the reference
        # to a shared object available any more later.
        reference.at_relations_content_uid = obj.UID()

        if self.isPrimary():
            obj.at_primary_ruleset = self.getRuleset().getId()
        
            
        reference.addReference(obj, RELATIONSHIP_CONTENTREF)

    def finalizeOnDisconnect(self, reference, chain):
        pass

    def listActionsFor(self, reference):
        value = []
        checkPermission = getSecurityManager().checkPermission
        for obj in reference.getContentObjects():
            if checkPermission(CMFCorePermissions.View, obj):
                value.append({'title': obj.title_or_id(),
                              'url': obj.absolute_url(),
                              'icon': obj.getIcon(1)})
        return value

    def _lookForSharedObject(self, reference, chain):
        if not self.getShareWithInverse(): return

        ii = _findInstanceOf(self.getRuleset().objectValues(),
                             inverse.InverseImplicator)
        if ii:
            iRuleset = ii.getInverseRuleset()
            key = _makeKey(
                iRuleset.getId(),
                reference.targetUID,
                reference.sourceUID,
                self.getPortalType())
            return chain[self.__class__.__name__].get(key)

    # AT implementation
    schema = BaseSchemaWithInvisibleId + Schema((
        StringField('portalType',
                    vocabulary='_availableTypesVocabulary',
                    enforceVocabulary=True,
                    required=True,
                    widget=SelectionWidget(label='Portal Type',
                                       label_msgid='label_relation_portaltype',
                                       description="Select a Portal Type from the list.",
                                       description_msgid='help_relation_portaltype',
                                       i18n_domain='Relations',),),

        BooleanField('shareWithInverse',
                    default=True,
                    widget=BooleanWidget(label='Share with Inverse?',
                                       label_msgid='label_relation_shareinverse',
                                       #description="A description...",
                                       #description_msgid='help_relation_shareinverse',
                                       i18n_domain='Relations',),),

        BooleanField('primary',
                    accessor='isPrimary',
                    widget=BooleanWidget(label='Is Primary?',
                                       label_msgid='label_relation_primary',
                                       #description="A description...",
                                       #description_msgid='help_relation_primary',
                                       i18n_domain='Relations',),),
        ))
    portal_type = 'Content Reference'

    def _availableTypesVocabulary(self):
        return DisplayList(
            [(pt, pt) for pt in utils.getReferenceableTypes(self)])

registerType(ContentReferenceFinalizer, PROJECTNAME)
