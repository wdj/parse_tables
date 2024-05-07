#!/usr/bin/env python3
"""============================================================================

Handle Adverbs table from Ontology.mdb file.

============================================================================"""

import _utils
from ontology_adpositions import OntologyAdpositions

#==============================================================================

class OntologyAdverbs(OntologyAdpositions):
    """
    Handle Adverbs table from Ontology.mdb file.

    Most functionality is provided by base class.
    """

    RULE_TYPE = _utils.RULE_TYPES['Ontology_Adverbs']

#==============================================================================
