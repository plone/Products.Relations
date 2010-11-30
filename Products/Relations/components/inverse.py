from Acquisition import ImplicitAcquisitionWrapper, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.public import *
from Products.Archetypes.ReferenceEngine import Reference
from Products.Archetypes.utils import make_uuid

from Products.Relations.config import *
from Products.Relations import interfaces, ruleset, utils
from Products.Relations.schema import BaseSchemaWithInvisibleId

# Maybe some day we will get consistency on how implements works
# so that we don't have to do this - cwarner
from zope.interface import implements
from Products.Archetypes.interfaces import IBaseContent
from Products.Archetypes.interfaces import IReferenceable
from Products.Archetypes.interfaces import IExtensibleMetadata

_invref_attr = '_relations_invref_uid'
_proc_marker_attr = '_v_relations_process_invref'

class InverseImplicator(BaseContent, ruleset.RuleBase):
    """Implicator that creates a reference from target to source."""
    implements(interfaces.IImplicator, IBaseContent, IReferenceable, IExtensibleMetadata)

    content_icon = 'inverseimplicator_icon.gif'

    def implyOnConnect(self, reference, chain):
        iRuleset = self.getInverseRuleset()

        if iRuleset is not None and not hasattr(reference, _proc_marker_attr):
            added_index = len(chain.added)

            iRuleset.implyOnConnect(reference.getTargetBrain(),
                                    reference.getSourceBrain(),
                                    chain, metadata={_proc_marker_attr: True})
            
            invRef = chain.added[added_index]
            setattr(reference, _invref_attr, invRef.UID())
            setattr(invRef, _invref_attr, reference.UID())

    def implyOnDisconnect(self, reference, chain):
        mykey = '%s:disconnected' % self.__class__.__name__
        ref_catalog = getToolByName(self, REFERENCE_CATALOG)

        iRuleset = self.getInverseRuleset()
        if iRuleset is not None and not reference.UID() in chain[mykey]:
            chain[mykey][reference.UID()] = reference # avoid recursion
            invRefUID = getattr(reference, _invref_attr)
            brains = ref_catalog(UID=invRefUID)
            if brains:
                invRef = brains[0].getObject()
                iRuleset.implyOnDisconnect(invRef, chain)                

    # Archetypes implementation
    schema = BaseSchemaWithInvisibleId + Schema((
        ReferenceField('inverseRuleset',
                       relationship='inverseRuleset',
                       allowed_types_method='_allowedTypesRuleset',
                       widget=ReferenceWidget(label='Inverse Ruleset',
                                       label_msgid='label_relation_inverseruleset',
                                       #description="A description...",
                                       #description_msgid='help_inverseruleset',
                                       i18n_domain='Relations',),),
        ))
    portal_type = 'Inverse Implicator'

    def _allowedTypesRuleset(self, instance):
        return utils.getPortalTypesByInterfaces(self, ('IRuleset',))

    def getInverseRuleset(self):
        inv = self.getRefs('inverseRuleset')
        if inv:
            return inv[0]
        else:
            return None

registerType(InverseImplicator, PROJECTNAME)                       
        

    
