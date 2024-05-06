#!/usr/bin/env python3
"""============================================================================

Handle Rules_FindReplace table from <MyLanguage>.mdb file.

============================================================================"""

import re

import _utils
from _input_structures import *

#==============================================================================

class RulesFindReplace:
    """
    Handle Rules_FindReplace table from <MyLanguage>.mdb file.

    -----------------------------------------------------------------------
    Notes

see:
ExecuteRules.cpp, lines 16683f
CTA1Doc::GetIdiomRule

    -----------------------------------------------------------------------
    """

    RULE_TYPE = _utils.RULE_TYPES['Rules_FindReplace']

    # List of fields that are needed for the translation/generation.

    FIELDNAMES_IMPT = [
        'Status',
        'SyntacticCategory',
        'RuleType',
        'Input',
        'Output',
        'PunctuationTable',
    ]

    # Define all fields associated wtih this table.

    FIELDNAMES = [
        'ID', # it would seem this not needed for translation
        'GroupName', # ??? is this needed for the translation
        'RulesName', # this is human-readable, seems not needed for translation
        'Comment',
        'CommentFonts',
        'References',
        'NameFonts',
        'GrammarTopics',
    ] + FIELDNAMES_IMPT

#------------------------------------------------------------------------------

    def __init__(self):
        """Constructor for class."""

        self._is_set = False

#------------------------------------------------------------------------------

    def import_table(self, table: str):
        """
        Import and parse the table.
        The input is a list of rows, each row is a list of fields.

        NOTE: ordering of records for a rule is not based on ID but on the
        inherent order of records in the given table (recordset) in the file.
        """

        # Make some quick checks.
        assert len(table) >= 1, 'Error: malformed input table.'
        table_header = table[0]
        # Check table header (field names) correctness.
        assert len(table_header) == len(self.FIELDNAMES)
        # Are all fields present, even if in different order.
        assert set(table_header) == set(self.FIELDNAMES)

        # Number of rules = number of rows minus 1 for header (fieldnames)
        self._num_rules = len(table) - 1

        # Need this because order of fields is not guaranteed.
        sfoo = self._fieldnames_order_orig = table_header.copy()

        # Now parse rules (one per table record) one by one.

        self._rules = []

        for i in range(self._num_rules):

            # Parse rule.

            rule = {}

            # Copy all "unimportant" rule fields
            # (= those with no impact on translation/generation result).
            for fieldname in self.FIELDNAMES:
                if fieldname not in self.FIELDNAMES_IMPT:
                    j = sfoo.index(fieldname)
                    rule[fieldname] = table[i+1][j]

            # Is the rule set to "active" (to be used when translating).
            field = rule['Status'] = table[i+1][sfoo.index('Status')]
            assert field in ['0', '1']

            # What is the syncat of the word that gets the clitic.
            field = rule['SyntacticCategory'] = (
                table[i+1][sfoo.index('SyntacticCategory')])
            # ISSUE: the following could possibly be made more restrictive.
            # ISSUE: does this need to account for user-defined syncats.
            assert field in _utils.SYNTACTIC_CATEGORIES.values()


            # 0=Standard, 1=Punctuation
            field = rule['RuleType'] = table[i+1][sfoo.index('RuleType')]
            # NOTE: CTA1Doc::GetIdiomRule shows "" folds to "0"
            assert field in ['', '0', '1']
            is_punctuation = field == '1'

            # Standard case: "|"-delimited source strings for replacement
            # these substrings are scanned right-to-left for match.
            # preceding "||" instead of "|" denotes "bleeding" text,
            # which means stop scanning if match with that string found.
            # Punctuation case: puctuation marks for which to
            # "Delete Spaces Before" (stored concatented together)
            field = rule['Input'] = table[i+1][sfoo.index(
                         'Input')]

            # Standard case: matching, but target case instead of source.
            # Punctuation case: similar, "Delete Spaces After".
            field = rule['Output'] = table[i+1][sfoo.index(
                         'Output')]

            # Standard case: empty
            # Punctuation case: table rows are delimited (and final one
            #  terminated) by "\r\n".
            # Each row is Input String, then "~!~", then Output String,
            # then "~!~", then Comment.
            # NOTE: this could cause parsing problems if the punctuation
            # looks like "~!" for example.
            field = rule['PunctuationTable'] = table[i+1][sfoo.index(
                         'PunctuationTable')]
            rule['PunctuationTable'] = [f.split('~!~') if f != '' else []
                for f in field.split('\r\n')] if is_punctuation else field

            self._rules.append(rule)

        self._is_set = True

#------------------------------------------------------------------------------

    def export_table(self) -> str:
        """Convert the parsed table back into string form."""

        assert self._is_set, (
           'Error: cannot export because table has not been set.')

        result = []

        # Loop over table lines.
        for i in range(1+self._num_rules):
            result.append([])
            for j in range(len(self._fieldnames_order_orig)):
                k = self.FIELDNAMES.index(self._fieldnames_order_orig[j])
                fieldname = self.FIELDNAMES[k]
                rule_type = '' if i == 0 else self._rules[i-1]['RuleType']
                is_punctuation = rule_type == '1'

                # Pick up field from either the header or the rule.
                field = fieldname if i==0 else self._rules[i-1][fieldname]

                # Correct entries that have had special parsing.

                if i != 0 and fieldname == 'PunctuationTable':

                    field = '\r\n'.join(['~!~'.join(f) if f != [] else ''
                        for f in field]) if is_punctuation else field

                # Add field value to output.
                result[-1].append(field)

        return result

#==============================================================================
