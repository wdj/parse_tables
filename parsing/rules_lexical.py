#!/usr/bin/env python3
"""============================================================================

Handle Rules_Lexical table from <MyLanguage>.mdb file.

============================================================================"""

import _utils
from rules_spellout import RulesSpellout

#==============================================================================

class RulesLexical(RulesSpellout):
    """
    Handle Rules_Lexical table from <MyLanguage>.mdb file.

    Most functionality is provided by base class.
    """

    RULE_TYPE = _utils.RULE_TYPES['Rules_Lexical']

    # List of fields that are needed for the translation/generation.

    FIELDNAMES_IMPT = [
        'Status',
        'SyntacticCategory',
        'FormName',
        'RuleType',
        'RulesParsing',
        'Modification',
        'BaseForm',
        'Morpheme',
        'InfixParsing',
        'TriggerWords',
        'ExtraMorpheme',
    ]

    FIELDNAMES = [
        'ID', # it would seem this not needed for translation
        'RulesName', # this is human-readable, seems not needed for translation
        'Comment',
        'CommentFonts',
        'NameFonts',
        'GrammarTopics',
        'TableComments',
    ] + FIELDNAMES_IMPT

#==============================================================================
