# Set up permissions
from Products.CMFCore.permissions import setDefaultRoles 

ManageContentRelations = 'Relations: Manage content relations'
setDefaultRoles(ManageContentRelations, ('Manager','Owner'))

