## Script (Python) "relations_adddelete_vocab.py"
##parameters=test_only=0, ruleset_ids=None
##title=Make Relations vocabularies by querying all rulesets.
##bind context=context
##bind container=container
##

# This script just become an alias for the utils.adddeleteVocab
# function.

from Products.Relations.utils import adddeleteVocab

return adddeleteVocab(context, test_only, ruleset_ids)
