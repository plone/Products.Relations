from AccessControl import ModuleSecurityInfo
modulesec = ModuleSecurityInfo('Products.Relations.exception')
modulesec.declarePublic('ValidationException')


class ValidationException(Exception):

    __allow_access_to_unprotected_subobjects__ = 1
    
    def __init__(self, message, reference=None, chain=None):
        self.message = message
        self.reference = reference
        self.chain = chain

        self.args = self.message, self.reference

