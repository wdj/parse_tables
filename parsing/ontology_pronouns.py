#!/usr/bin/env python3
"""============================================================================

Handle Pronouns table from Ontology.mdb file.

============================================================================"""

import _utils
from ontology_adpositions import OntologyAdpositions

#==============================================================================

class OntologyPronouns(OntologyAdpositions):
    """
    Handle Pronouns table from Ontology.mdb file.

    Most functionality is provided by base class.
    """

    RULE_TYPE = _utils.RULE_TYPES['Ontology_Pronouns']

#==============================================================================
