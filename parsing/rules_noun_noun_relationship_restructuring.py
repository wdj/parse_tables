#!/usr/bin/env python3
"""============================================================================

Handle Rules_NounNounRelationshipRestructuring table from <MyLanguage>.mdb file.

============================================================================"""

import _utils
from rules_transfer import RulesTransfer

#==============================================================================

class RulesNounNounRelationshipRestructuring(RulesTransfer):
    """
    Handle Rules_NounNounRelationshipRestructuring table from
   <MyLanguage>.mdb file.

    Most functionality is provided by base class.
    """

    RULE_TYPE = _utils.RULE_TYPES['Rules_NounNounRelationshipRestructuring']

#==============================================================================
