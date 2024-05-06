#!/usr/bin/env python3
"""============================================================================

Handle Source_UsersAdverbs table from <MyLanguage>.mdb file.

============================================================================"""

import _utils
from source_users_nouns import SourceUsersNouns

#==============================================================================

class SourceUsersAdverbs(SourceUsersNouns):
    """
    Handle Source_UsersAdverbs table from <MyLanguage>.mdb file.

    Most functionality is provided by base class.
    """

    RULE_TYPE = _utils.RULE_TYPES['Source_UsersAdverbs']

#==============================================================================
