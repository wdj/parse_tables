#!/usr/bin/env python3
"""============================================================================

Handle Rules_PhraseStructure table from <MyLanguage>.mdb file.

============================================================================"""

import re

import _utils
from _input_structures import *

#==============================================================================

class RulesPhraseStructure:
    """
    Handle Rules_PhraseStructure table from <MyLanguage>.mdb file.

    -----------------------------------------------------------------------
    Notes

see:
CPhraseStructureRuleDlg::DisplayRule
ExecuteRules.cpp, lines 16318f
CUtilities::BuildPSRConstituentName

    -----------------------------------------------------------------------
    """

    RULE_TYPE = _utils.RULE_TYPES['Rules_PhraseStructure']

    # List of fields that are needed for the translation/generation.

    FIELDNAMES_IMPT = [
        'Status',
        'SyntacticCategory',
        'Rule',
        'RulesFeatures',
        'InputStructure',
    ]

    # Define all fields associated wtih this table.

    FIELDNAMES = [
        'ID',
        'GroupName', # ??? is this needed for the translation
        'RulesName', # this is human-readable, seems not needed for translation
        'Comment',
        'CommentFonts',
        'References',
        'NameFonts',
        'GrammarTopics',
        'Cooccurrences',
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

            # Get Rule.
            field = rule['Rule'] = table[i+1][sfoo.index(
                         'Rule')]

            field = field.split('^')

            field2 = []
            for subfield in field:
                field2.append([])
                # Empty line.
                if subfield == '':
                    pass
                # Non leaf node.
                elif subfield[0] == '*':
                    # Non leaf node indicator
                    field2[-1].append(subfield[0])
                    # level (0=top branches)
                    field2[-1].append(subfield[1])
                    # node name (group name)
                    field2[-1].append(subfield[2:])
                # User defined syncat leaf node.
                elif subfield[0] == '&':
                    # user defined syncat indicator
                    field2[-1].append(subfield[0])
                    # syncat name, features (blank), example, (optional) name
                    field2[-1] += subfield[1:].split('|')
                # Non user defined leaf node.
                else:
                    # syncat id, features, example, (optional) name
                    field2[-1] += subfield.split('|')

            rule['Rule'] = field2

            # Specify features for match. Delimiter is "^"; 3 fields:
            # word features, phrase features, clause features.
            field = rule['RulesFeatures'] = (
                table[i+1][sfoo.index('RulesFeatures')].split('^'))

            # Parse the input structure.
            field = rule['InputStructure'] = import_input_structure(
                table[i+1][sfoo.index('InputStructure')],
                rule_type=self.RULE_TYPE)

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

                # Pick up field from either the header or the rule.
                field = fieldname if i==0 else self._rules[i-1][fieldname]

                # Correct entries that have had special parsing.

                if i != 0 and fieldname == 'Rule':

                    field2 = []

                    for subfield in field:
                        field2.append('')
                        if subfield == []:
                            pass
                        elif subfield[0] == '*':
                            field2[-1] += subfield[0]
                            field2[-1] += subfield[1]
                            field2[-1] += '|'.join(subfield[2:])
                        elif subfield[0] == '&':
                            field2[-1] += subfield[0]
                            field2[-1] += '|'.join(subfield[1:])
                        else:
                            field2[-1] += '|'.join(subfield)

                    field = '^'.join(field2)

                if i != 0 and fieldname == 'RulesFeatures':
                    field = '^'.join(field)

                if i != 0 and fieldname == 'InputStructure':
                    field = export_input_structure(field, 
                                                   rule_type=self.RULE_TYPE)

                # Add field value to output.
                result[-1].append(field)

        return result

#==============================================================================
