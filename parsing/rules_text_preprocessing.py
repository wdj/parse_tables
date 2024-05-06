#!/usr/bin/env python3
"""============================================================================

Handle Rules_TextPreprocessing table from <MyLanguage>.mdb file.

============================================================================"""

import _utils
from rules_transfer import RulesTransfer

#==============================================================================

class RulesTextPreprocessing(RulesTransfer):
    """
    Handle Rules_TextPreprocessing table from <MyLanguage>.mdb file.

    Most functionality is provided by base class.
    """

    # an extra field, apparently.
    # Appears not to be used by ExecuteRules.
    FIELDNAMES = RulesTransfer.FIELDNAMES + ['ExtraInfo']

    RULE_TYPE = _utils.RULE_TYPES['Rules_TextPreprocessing']

#==============================================================================
