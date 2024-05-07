#!/usr/bin/env python3
"""============================================================================

Handle Conjunctions table from Ontology.mdb file.

============================================================================"""

import _utils
from ontology_adpositions import OntologyAdpositions

#==============================================================================

class OntologyConjunctions(OntologyAdpositions):
    """
    Handle Conjunctions table from Ontology.mdb file.

    Most functionality is provided by base class.
    """

    RULE_TYPE = _utils.RULE_TYPES['Ontology_Conjunctions']

#==============================================================================
