## Controller Python Script "relations_form_validate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=id='',file=''
##title=Validates references by actually creating them
##
from Products.Relations.processor import process
from Products.Relations.exception import ValidationException

if state.getStatus() == 'failure': return state

catalog = context.reference_catalog

to_add = []
to_del = []

for field_id in context.REQUEST.get('all_fields', []):
    relationship = field_id[10:]
    my_uid = context.UID()
    new_uids = context.REQUEST.get(field_id) or []
    old_uids = [b.targetUID for b in catalog(sourceUID=my_uid,
                                       relationship=relationship)]

    for uid in new_uids:
        if uid not in old_uids:
            to_add.append((my_uid, uid, relationship))

    for uid in old_uids:
        if uid not in new_uids:
            to_del.append((my_uid, uid, relationship))

if not to_add and not to_del:
    return state.set(portal_status_message="Nothing to do.")
try:
    chain = process(context, to_add, to_del)
    return state.set(portal_status_message="Successfully updated references.")
except ValidationException, e:
    field_id = 'relations_%s' % e.reference.relationship
    state.setError(field_id, e.message)
    return state.set(status='failure',
                     portal_status_message="Please correct the indicated errors.")
