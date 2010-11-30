# Products initialization
from config import *
from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore.utils import ContentInit

# register skins directory
from Products.CMFCore.DirectoryView import registerDirectory
registerDirectory(SKINS_DIR, GLOBALS)

# BBB for Z2 vs Z3 interfaces checks, borrowed from Products.PloneFormGen
def implementedOrProvidedBy(anInterface, anObject):
    try:
        return anInterface.providedBy(anObject)
    except AttributeError:
        return anInterface.isImplementedBy(anObject)

def initialize(context):
    import ruleset
    import components

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

import brain, exception, processor, utils # contain ModuleSecurityInfo
import field # registers field

