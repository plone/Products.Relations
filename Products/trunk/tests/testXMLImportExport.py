import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from App.Common import package_home

from Products.PloneTestCase import PloneTestCase
from Products.Relations import config

import common
common.installWithinPortal()

class TestXMLImportExport(PloneTestCase.PloneTestCase):

    def testXMLImport(self):
        self.loginAsPortalOwner()
        xmlpath=os.path.join(
            package_home(config.GLOBALS), 'tests', 'relations_sample.xml')
        f=open(xmlpath)
        xml=f.read()
        f.close()
        
        tool=self.portal.relations_library
        tool.importXML(xml)
        ruleset=tool.getRuleset('document_files')
        
        #export it
        xml=tool.exportXML()

        #now reimport the junk again
        tool.manage_delObjects(tool.objectIds())
        tool.importXML(xml)

        # Make sure the imported ruleset contains the same set of components
        self.assertEqual(tool.getRuleset('document_files').objectIds(), ruleset.objectIds())
        
        # check if the inverse Implicator is imported properly.
        # this made problems.
        rset = tool.getRuleset('document_files')
        from Products.Relations.components.contentreference import _findInstanceOf
        from Products.Relations.components import inverse
        ii = _findInstanceOf(rset.objectValues(), inverse.InverseImplicator)    
        


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestXMLImportExport))
    return suite

if __name__ == '__main__':
    framework()
