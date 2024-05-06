#!/usr/bin/env python3
"""============================================================================

Handle Verb_Mappings_English table from <MyLanguage>.mdb file.

============================================================================"""

import _utils
from adposition_mappings_english import AdpositionMappingsEnglish

#==============================================================================

class VerbMappingsEnglish(AdpositionMappingsEnglish):
    """
    Handle Verb_Mappings_English table from <MyLanguage>.mdb file.

    Most functionality is provided by base class.
    """

    RULE_TYPE = _utils.RULE_TYPES['Verb_Mappings_English']

#==============================================================================
