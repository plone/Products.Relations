# -*- coding: utf-8 -*-
#
# Copyright (c) 2006-2007 by BlueDynamics Alliance, Klein & Partner KEG, Austria
#
# German Free Software License (D-FSL)
#
# This Program may be used by anyone in accordance with the terms of the 
# German Free Software License
# The License may be obtained under <http://www.d-fsl.org>.
#

__author__ = """Jens Klein <jens@bluedynamics.com>"""
__docformat__ = 'plaintext' 

from zope.interface import implements, Interface, Attribute
 
class IRelationEvent(Interface):
    """An generic event related to a Relation.

    The references are all from one single Relation.
    """
    context = Attribute("The context")
    references = Attribute("A list of references")


class IRelationConnectedEvent(IRelationEvent):
    """An event related to a Relation connection."""


class IRelationDisconnectedEvent(IRelationEvent):
    """An event related to a Relation disconnection."""

    
class RelationEvent(object):
    """connect happend."""
    implements(IRelationEvent)

    def __init__(self, context, references):
        self.context = context
        self.references = references

class RelationConnectedEvent(RelationEvent):
    """connect happend."""

    implements(IRelationConnectedEvent)


class RelationDisconnectedEvent(RelationEvent):
    """disconnect happend."""

    implements(IRelationDisconnectedEvent)
