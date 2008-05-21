## Controller Python Script "relations_form_security"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Check for permissions to relations_form.
##
mtool = context.portal_membership
if not mtool.checkPermission('Relations: Manage content relations', context):
    state.set(status='failure',
              portal_status_message="Insufficient privileges.")
return state
