This repository is archived and read only.

If you want to unarchive it, then post to the [Admin & Infrastructure (AI) Team category on the Plone Community Forum](https://community.plone.org/c/aiteam/55).

Relations Readme

  Overview

    Relations allows for the definition of sets of rules for
    validation, creation and lifetime of Archetypes references.
    Contained in each ruleset are components that make for the actual
    rules logic.

    Rulesets may be created and edited through the web (TTW).
    Components implementing custom behaviour are easily added.

  Installation

    In Plone, click "Add/Remove Products" in the Plone Setup. Then select
    Relations from the list of available products and click "Install".

    Now click "Relations Library" in the Plone Setup portlet on the
    left to visit the TTW configuration user interface.

  Usage

    As an example, add a ruleset by clicking "Add Ruleset" in the
    library.  Now choose a reasonable identification.  Notice that
    identifications are required to be unique among rulesets in your
    portal.

    Note: When you create a reference through a ruleset, the
    relationship attribute of the reference is set to be the ruleset's
    id.  There's nothing that is different about how you use the
    Archetypes Reference API when querying for referenced objects.
    (However, references are created and deleted differently; namely
    through function 'processor.process'.)

    The ruleset's title is what is presented to the user in Plone.
    Let's choose "Is Child Of" as the title of our ruleset, and
    "isChildOf" as the identification.

    After saving changes, click "Add New Item" and add a cardinality
    constraint.  Enter "Exactly Two" as the title and choose "2" for
    both the minimum and the maximum number of targets.
    
    At this point we still need another component so we can actually
    make use of the "Is Child Of" ruleset.  Add a "Portal Type
    Constraint" and choose "Unrestricted" as its title.  Click the
    "Save" button and then the "Relations" tab that just appeared.
    The form says "Edit Relations for Unrestricted", meaning that we
    can from here add and remove "Is Child Of" references from our
    Portal Type Constraint "Unrestricted" to any referenceable portal
    object.

    Through our "Exactly Two" constraint we assert that we have
    exactly two "parents".

  Requirements

    Archetypes >= 1.4.0
    Python 2.4

  See also

    Additional documentation is in the product's doc/ directory on the
    filesystem.

  Credits

    This code was created for the ZUCCARO project.  ZUCCARO is a
    database framework for the Humanities developed by the Bibliotheca
    Hertziana, Max-Planck Institute for Art History.  For further
    information, please visit http://zuccaro.biblhertz.it/
