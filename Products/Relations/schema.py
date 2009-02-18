"""Archetypes schema definitions for ruleset module, and other common
schemas."""

from Products.Archetypes.public import *

BaseSchemaWithInvisibleId = BaseSchema.copy()
BaseSchemaWithInvisibleId['id'].widget.visible = {'edit': 'hidden',
                                                  'view': 'invisible'}
def RulesetSchema():
    schema = BaseSchema.copy()
    id_widget_attrs = {
        'description':
        "Relationship attribute for references created through this ruleset.",
        'description_msgid': None,
        'label': "Identification",
        }
    schema['id'].widget.__dict__.update(id_widget_attrs)
    schema['id'].required = 1

    cf = TextField('about',
                   default_content_type = 'text/restructured',
                   default_output_type = 'text/html',
                   allowable_content_types = ('text/structured',
                                              'text/restructured',
                                              'text/plain-pre'),
                   widget=TextAreaWidget(rows=8, 
                                       label='About',
                                       label_msgid='label_relation_about',
                                       description="Information about this Ruleset",
                                       description_msgid='help_relation_about',
                                       i18n_domain='Relations',),)

    schema.addField(cf)

    return schema
    
RulesetSchema = RulesetSchema()
