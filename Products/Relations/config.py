from Products.CMFCore.permissions import AddPortalContent, ManagePortal
from Products.Archetypes import config as ATconfig


ADD_CONTENT_PERMISSION = AddPortalContent

PROJECTNAME = 'Relations'
SKINS_DIR = 'skins'

GLOBALS = globals()

DEPS = 'Archetypes',

UID_CATALOG = ATconfig.UID_CATALOG
REFERENCE_CATALOG = ATconfig.REFERENCE_CATALOG

# after how many rulesets do we want a subtransaction?
IMPORT_TRANSACTION_STEPPING = 15

#tools
RELATIONS_LIBRARY = 'relations_library'

# relationships
RELATIONSHIP_LIBRARY = 'Relations.library'
RELATIONSHIP_RULESETTOREF = 'Relations.rulesettoref'
RELATIONSHIP_CONTENTREF = 'Relations.contentref'

# set to 1 by tests.common
INSTALL_TEST_TYPES = 0

# set this to 1 if you want to allow more than one reference per
# triple.  your archetypes version might not support this!
ALLOW_MULTIPLE_REFS_PER_TRIPLE = 0

CONFIGLETS = (
    {'id': RELATIONS_LIBRARY,
     'name': 'Relations: Library',
     'action': 'string:${portal_url}/%s/' % RELATIONS_LIBRARY,
     'category': 'Products',
     'permission': ManagePortal,
     'imageUrl': 'book_icon.gif',
     'appId': 'Products.Relations',
     },
    )
