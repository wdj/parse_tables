#!/usr/bin/env python3
"""============================================================================

Handle Partciles table from Ontology.mdb file.

============================================================================"""

import _utils
from ontology_adpositions import OntologyAdpositions

#==============================================================================

class OntologyParticles(OntologyAdpositions):
    """
    Handle Particles table from Ontology.mdb file.

    Most functionality is provided by base class.
    """

    RULE_TYPE = _utils.RULE_TYPES['Ontology_Particles']

#==============================================================================
