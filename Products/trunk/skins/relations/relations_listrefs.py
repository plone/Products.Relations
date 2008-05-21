## Script (Python) "relations_listrefs.py"
##parameters=
##title=List all existing references, along with actions.
##bind context=context
##bind container=container
##

value = []

library = context.relations_library
ruleset_ids = [ruleset.getId() for ruleset in library.getRulesets()]

for ref in context.getReferenceImpl():
    if ref.relationship in ruleset_ids:
        ruleset = library.getRuleset(ref.relationship)
        value.append({
            'reference': ref,
            'ruleset': ruleset,
            'actions': ruleset.listActionsFor(ref)
            })

value.sort(lambda a,b:
           cmp(ruleset_ids.index(a['ruleset'].getId()),
               ruleset_ids.index(b['ruleset'].getId()))
           )
return value
        
    
