#!/usr/bin/env python3
"""============================================================================

Handle Conjunction_Mappings_English table from <MyLanguage>.mdb file.

============================================================================"""

import _utils
from adposition_mappings_english import AdpositionMappingsEnglish

#==============================================================================

class ConjunctionMappingsEnglish(AdpositionMappingsEnglish):
    """
    Handle Conjunction_Mappings_English table from <MyLanguage>.mdb file.

    Most functionality is provided by base class.
    """

    RULE_TYPE = _utils.RULE_TYPES['Conjunction_Mappings_English']

#==============================================================================
