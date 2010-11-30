from Products.PloneTestCase import PloneTestCase
from Products.CMFCore.utils import getToolByName

from Products.Relations.config import *

# eases setting breakpoints for pdb
import os, sys
sys.path.append('%s/Products' % os.environ['INSTANCE_HOME'])

# make Zope products available to test environment
product_dependencies = [PROJECTNAME]

def installProducts():
    for product in product_dependencies:
        PloneTestCase.installProduct(product)

def installWithinPortal():
    # Import to install the sample types
    from Products.Archetypes.tests import attestcase
    
    installProducts()
    PloneTestCase.setupPloneSite(products=product_dependencies, 
        extension_profiles=('Products.Archetypes:Archetypes_sampletypes',))

def createObjects(testcase, names):
    """Given a testname and a list of portal types "names", I will create
    in testcase.folder objects that correspond to the given names, with their
    ids set to their type names.

    Returns the list of objects created."""
    value = []

    for t in names:
        testcase.folder.invokeFactory(t, t)
        obj = getattr(testcase.folder, t)
        value.append(obj)

    return value

def createRuleset(testcase, id):
    """Creates a ruleset and registers it. Returns the new ruleset."""
    ttool = getToolByName(testcase.portal, 'portal_types')
    construct = ttool.constructContent
    construct('Ruleset', testcase.folder, id)

    ruleset = getattr(testcase.folder, id)
    library = getToolByName(testcase.portal, RELATIONS_LIBRARY)
    library.registerRuleset(ruleset)

    return ruleset
