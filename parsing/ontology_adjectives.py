#!/usr/bin/env python3
"""============================================================================

Handle Adjectives table from Ontology.mdb file.

============================================================================"""

import _utils
from ontology_adpositions import OntologyAdpositions

#==============================================================================

class OntologyAdjectives(OntologyAdpositions):
    """
    Handle Adjectives table from Ontology.mdb file.

    Most functionality is provided by base class.
    """

    RULE_TYPE = _utils.RULE_TYPES['Ontology_Adjectives']

    # List of fields that are needed for the translation/generation.
    
    FIELDNAMES_IMPT = [
        'Roots',
        'Categories',
        'Level',
        'ParentID',
    ]
    
    # Define all fields associated wtih this table.
    
    FIELDNAMES = [
        'ID', # Need only in order to sort records into proper order.
        'Glosses',
        'Occurrences',
        'Comments',
        'LN Base',
        'LN Sense',
        'LN Gloss',
        'LN Definition',
        'LN Note',
        'LN Tag',
        'Examples',
        'Exhaustive Examples',
        'Expansion Rule',
        'Expansion Rule Status',
        'Distribution',
        'Brief Gloss',
        'Linguists Assistant',
    ] + FIELDNAMES_IMPT


#==============================================================================
