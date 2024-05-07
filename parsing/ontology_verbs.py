#!/usr/bin/env python3
"""============================================================================

Handle Verbs table from Ontology.mdb file.

============================================================================"""

import _utils
from ontology_adpositions import OntologyAdpositions

#==============================================================================

class OntologyVerbs(OntologyAdpositions):
    """
    Handle Verbs table from Ontology.mdb file.

    Most functionality is provided by base class.
    """

    RULE_TYPE = _utils.RULE_TYPES['Ontology_Verbs']

#==============================================================================
