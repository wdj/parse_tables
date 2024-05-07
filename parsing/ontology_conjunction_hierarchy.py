#!/usr/bin/env python3
"""============================================================================

Handle ConjunctionHierarchy table from Ontology.mdb file.

============================================================================"""

import _utils
from ontology_adjective_hierarchy import OntologyAdjectiveHierarchy

#==============================================================================

class OntologyConjunctionHierarchy(OntologyAdjectiveHierarchy):
    """
    Handle ConjunctionHierarchy table from Ontology.mdb file.

    Most functionality is provided by base class.
    """

    RULE_TYPE = _utils.RULE_TYPES['Ontology_ConjunctionHierarchy']

#==============================================================================
