#!/usr/bin/env python3
"""============================================================================

Handle Pronoun_Mappings_English table from <MyLanguage>.mdb file.

============================================================================"""

import _utils
from adposition_mappings_english import AdpositionMappingsEnglish

#==============================================================================

class PronounMappingsEnglish(AdpositionMappingsEnglish):
    """
    Handle Pronoun_Mappings_English table from <MyLanguage>.mdb file.

    Most functionality is provided by base class.
    """

    RULE_TYPE = _utils.RULE_TYPES['Pronoun_Mappings_English']

#==============================================================================
