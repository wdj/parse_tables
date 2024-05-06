#!/usr/bin/env python3
"""============================================================================

Handle Adjective_Mappings_English table from <MyLanguage>.mdb file.

============================================================================"""

import _utils
from adposition_mappings_english import AdpositionMappingsEnglish

#==============================================================================

class AdjectiveMappingsEnglish(AdpositionMappingsEnglish):
    """
    Handle Adjective_Mappings_English table from <MyLanguage>.mdb file.

    Most functionality is provided by base class.
    """

    RULE_TYPE = _utils.RULE_TYPES['Adjective_Mappings_English']

    # List of fields that are needed for the translation/generation.

    FIELDNAMES_IMPT = [
        'Mappings',
        'Collocation Correction Rule',
        'Convert To Verb',
    ]

    # Define all fields associated wtih this table.

    FIELDNAMES = [
        'ID', # it would seem this not needed for translation
        'Comment',
        'Comment Fonts',
        'Expansion Rule',
        'Expansion Rule BreakPoint',
        'Expansion Rule Status',
    ] + FIELDNAMES_IMPT

#==============================================================================
