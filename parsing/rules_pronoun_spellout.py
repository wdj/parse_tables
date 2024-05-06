#!/usr/bin/env python3
"""============================================================================

Handle Rules_PronounSpellout table from <MyLanguage>.mdb file.

============================================================================"""

import _utils
from rules_spellout import RulesSpellout

#==============================================================================

class RulesPronounSpellout(RulesSpellout):
    """
    Handle Rules_PronounSpellout table from <MyLanguage>.mdb file.

    Most functionality is provided by base class.
    """

    RULE_TYPE = _utils.RULE_TYPES['Rules_PronounSpellout']

#==============================================================================
