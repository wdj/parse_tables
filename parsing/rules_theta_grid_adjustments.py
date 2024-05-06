#!/usr/bin/env python3
"""============================================================================

Handle Rules_ThetaGridAdjustments table from <MyLanguage>.mdb file.

============================================================================"""

import _utils
from rules_transfer import RulesTransfer

#==============================================================================

class RulesThetaGridAdjustments(RulesTransfer):
    """
    Handle Rules_ThetaGridAdjustments table from <MyLanguage>.mdb file.

    Most functionality is provided by base class.
    """

    # an extra field, apparently.
    FIELDNAMES = RulesTransfer.FIELDNAMES + ['Unnecessary']

    RULE_TYPE = _utils.RULE_TYPES['Rules_ThetaGridAdjustments']

#==============================================================================
