from AccessControl import ModuleSecurityInfo
from Acquisition import aq_base
from Globals import InitializeClass
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.ReferenceEngine import Reference
from Products.Archetypes.utils import shasattr

from config import *
import brain
import interfaces

modulesec = ModuleSecurityInfo('Products.Relations.brain')
modulesec.declarePublic('makeBrainAggregate')

_marker = ()

class BrainAggregate:
    """Catalog brain kind of object that aggregates metadata from multiple
    catalogs."""

    __implements__ = interfaces.IBrainAggregate,
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, brain, sources):
        self.brain = brain
        self.sources = sources

    def __getitem__(self, key): # extend brain's __getitem__
        attr = getattr(aq_base(self), key, _marker)
        if attr is not _marker:
            return getattr(self, key)
        else:
            raise KeyError, key

    def __getattr__(self, key):
        attr = getattr(aq_base(self.brain), key, _marker)
        if attr is not _marker:
            return getattr(self.brain, key)
        else:
            raise AttributeError, key

    def __repr__(self):
        return "<Brain aggregate with UID: %s, path: %s>" % \
               (self.brain.UID, self.brain.getPath())

    def __eq__(self, other):
        if interfaces.IBrainAggregate.isImplementedBy(other):
            return self.brain.UID == other.brain.UID and \
                   self.sources == other.sources

def makeBrainAggregate(context, obj):
    """Returns a brain aggregate that corresponds to obj.

    obj may be either a UID string, a brain of uid_catalog or an aggregated
    brain."""

    if interfaces.IBrainAggregate.isImplementedBy(obj):
        return obj
    elif isinstance(obj, type('')): # assume a UID
        return makeBrainAggrFromUID(context, obj)
    elif shasattr(obj, 'getPath'): # assume uid_catalog brain
        return makeBrainAggrFromBrain(context, obj)
    else:
        raise ValueError, "Object %r must be either UID or brain." % obj

def makeBrainAggrFromUID(context, uid, catalogs=None):
    uc = getToolByName(context, UID_CATALOG)
    brain = uc(UID=uid)[0]
    return makeBrainAggrFromBrain(context, brain, catalogs)

def makeBrainAggrFromBrain(context, brain, catalogs=None):
    if catalogs is None: # query archetype_tool
        at = getToolByName(context, 'archetype_tool')
        # XXX portal_type must equal meta_type for this to work
        sources = at.getCatalogsByType(brain.portal_type)

    else: # go with the list of provided catalog ids
        sources = [getToolByName(context, cid) for cid in catalogs]
        
    sources = [s for s in sources if s.getId() != UID_CATALOG]
    aggr = BrainAggregate(brain, [s.getId() for s in sources])
    portal_url = getToolByName(context, 'portal_url')
    # uid catalog uses relative urls, we assume all others use absolute
    abs_path = '/%s/%s' % (portal_url(relative=1), brain.getPath())
    for s in sources:
        try:
            aggr.__dict__.update(s.getMetadataForUID(abs_path))
        except KeyError:
            continue # we have to tolerate this exception, because by
                     #default some objects (e.g. .personal) are not indexed in
                     #portal_catalog 
                     
            #raise KeyError, ("Unable to fetch metadata for UID %s from %s." %
            #                 (abs_path, s.getId()))
    return aggr

class ReferenceWithBrains(Reference):
    __implements__ = interfaces.IReferenceWithBrains

# These proxy methods all make use of a volatile attribute to store their value
# The dict maps method names, e.g. 'getSourceBrain', to functions that produce
# the value.
proxies = {
    'getSourceBrain':
    lambda self: brain.makeBrainAggregate(self, self.sourceUID),
           
    'getTargetBrain':
    lambda self: brain.makeBrainAggregate(self, self.targetUID),

    'getSourceObject':
    lambda self: Reference.getSourceObject(self),

    'getTargetObject':
    lambda self: Reference.getTargetObject(self),
    }

def makeProxyMethod(key, valueFun):
    def proxyMethod(self):
        attr_name = '_v_%s' % key
        if not shasattr(self, attr_name):
            setattr(self, attr_name, valueFun(self))
        return getattr(self, attr_name)
    return proxyMethod

for key, valueFun in proxies.items():
    setattr(ReferenceWithBrains, key, makeProxyMethod(key, valueFun))
# end of class ReferenceWithBrains

InitializeClass(ReferenceWithBrains)
