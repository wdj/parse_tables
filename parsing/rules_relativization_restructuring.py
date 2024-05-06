#!/usr/bin/env python3
"""============================================================================

Handle Rules_RelativizationRestructuring table from <MyLanguage>.mdb file.

============================================================================"""

import _utils
from rules_transfer import RulesTransfer

#==============================================================================

class RulesRelativizationRestructuring(RulesTransfer):
    """
    Handle Rules_RelativizationRestructuring table from <MyLanguage>.mdb
    file.

    Most functionality is provided by base class.
    """

    RULE_TYPE = _utils.RULE_TYPES['Rules_RelativizationRestructuring']

#==============================================================================
