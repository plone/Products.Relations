from StringIO import StringIO
from Products.CMFCore.utils import getToolByName

def installConfiglets(self, d):
    out = StringIO()
    cp = getToolByName(self, 'portal_controlpanel', None)
    if cp is not None:
        existing = [cfglet['id'] for cfglet in
                    cp.enumConfiglets(group='Products')]
        for configlet in d:
            if configlet['id'] not in existing:
                cp.registerConfiglet(**configlet)
                print >> out, "Installed configlet: %s" % configlet['id']
    else:
        print >> out, ("portal_controlpanel not found. " 
                       "No configlets registered.")
    return out.getvalue()

def uninstallConfiglets(self, d):
    out = StringIO()
    cp = getToolByName(self, 'portal_controlpanel', None)
    if cp is not None:
        for configlet in d:
            cp.unregisterConfiglet(configlet['id'])
        print >> out, "Configlets unregistered."
    return out.getvalue()

            
