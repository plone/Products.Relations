from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getFSVersionTuple
from Products.Relations.config import PROJECTNAME


def install(self):
    out = StringIO()

    tool=getToolByName(self, "portal_setup")

    if getFSVersionTuple()[:3]>=(3,0,0):
        tool.runAllImportStepsFromProfile(
                "profile-Products.Relations:default",
                purge_old=False)
    else:
        plone_base_profileid = "profile-CMFPlone:plone"
        tool.setImportContext(plone_base_profileid)
        tool.setImportContext("profile-Products.Relations:default")
        tool.runAllImportSteps(purge_old=False)
        tool.setImportContext(plone_base_profileid)

    print >> out, "Successfully installed %s" % PROJECTNAME



# keep the old stuff around for now

from Products.Archetypes.public import listTypes
from Products.Archetypes.utils import shasattr
from Products.Archetypes.Extensions.utils import installTypes, install_subskin

from Products.Relations.config import *
import Products.Relations.ruleset as ruleset
import Products.Relations.Extensions.utils as utils


def install_tools(self, out):
    if shasattr(self, RELATIONS_LIBRARY):
        print >> out, "%r already existed." % RELATIONS_LIBRARY
        return
    pt = getToolByName(self, 'portal_types')
    pt.constructContent('Relations Library', self, RELATIONS_LIBRARY)
    library = getattr(self, RELATIONS_LIBRARY)
    t = pt.getTypeInfo('Relations Library').Title()
    library.setTitle(t)

    # hide tool inside navigation
    portal_props = getToolByName(self, 'portal_properties', None)
    if portal_props is not None:
        navtree_props = getattr(portal_props, 'navtree_properties', None)
        if navtree_props is not None:
            if not RELATIONS_LIBRARY in navtree_props.idsNotToList:
                navtree_props.manage_changeProperties(
                    idsNotToList = list(navtree_props.idsNotToList) + \
                                   [RELATIONS_LIBRARY] 
                )

    # register as ActionProvider
    at = getToolByName(self, 'portal_actions')
    at.addActionProvider(RELATIONS_LIBRARY)

    print >> out, "%s installed." % t

def install_dependencies(self, out):
    DEPS = 'Archetypes',
    qi = self.portal_quickinstaller
    qi.installProducts(DEPS)
    print >> out, "Installed dependencies: %s" % DEPS

def old_install(self):
    out = StringIO()

    install_dependencies(self, out)
    installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)
    install_subskin(self, out, GLOBALS)
    install_tools(self, out)
    print >> out, utils.installConfiglets(self, CONFIGLETS)

    print >> out, "Successfully installed %s." % PROJECTNAME
    return out.getvalue()

def old_uninstall(self):
    out = StringIO()
    # XXX: Why does QuickInstaller think we own Archetypes' portal objects?
    at = getattr(self.portal_quickinstaller, 'Archetypes')
    NO_REMOVE = [RELATIONS_LIBRARY] + at.portalobjects
    prod = getattr(self.portal_quickinstaller, PROJECTNAME)
    prod.portalobjects = [p for p in prod.portalobjects if p not in NO_REMOVE]
    print >> out, utils.uninstallConfiglets(self, CONFIGLETS)

    # unregister as ActionProvider
    at = getToolByName(self, 'portal_actions')
    at.deleteActionProvider(RELATIONS_LIBRARY)

    print >> out, "Successfully uninstalled %s." % PROJECTNAME
    return out.getvalue()
