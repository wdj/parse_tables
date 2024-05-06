#!/usr/bin/env python3
"""============================================================================

Handle Adjectives table from <MyLanguage>.mdb file.

============================================================================"""

import _utils
from nouns import Nouns

#==============================================================================

class Adjectives(Nouns):
    """
    Handle Adjectives table from <MyLanguage>.mdb file.

    Most functionality is provided by base class.
    """

    RULE_TYPE = _utils.RULE_TYPES['Adjectives']

#==============================================================================
