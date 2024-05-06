#!/usr/bin/env python3
"""============================================================================

Handle Rules_FeatureCollapsing table from <MyLanguage>.mdb file.

============================================================================"""

import re

import _utils

#==============================================================================

class RulesFeatureCollapsing:
    """
    Handle Rules_FeatureCollapsing table from <MyLanguage>.mdb file.

    -----------------------------------------------------------------------
    Notes

    see CExecuteRules::PreprocessText (ExecuteRules.cpp, lines 22536f).

    the rule is a string of comma-separated values (with a comma at the end)
    each value is 2 characters: the feature value being collapsed to, then
    the feature value being collapsed.

    -----------------------------------------------------------------------
    """

    RULE_TYPE = _utils.RULE_TYPES['Rules_FeatureCollapsing']

    # List of fields that are needed for the translation/generation.

    FIELDNAMES_IMPT = [
        'SyntacticCategory',
        'FeatureName',
        'Rules',
    ]

    # Define all fields associated wtih this table.

    FIELDNAMES = [
        'ID', # it would seem this not needed for translation
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

            # What is syncat of the word whose feature value would be changed.
            field = rule['SyntacticCategory'] = (
                table[i+1][sfoo.index('SyntacticCategory')])
            # ISSUE: the following could possibly be made more restrictive.
            # ISSUE: does this need to account for user-defined syncats.
            assert field in _utils.SYNTACTIC_CATEGORIES.values()

            # What is the name of the feature whose value is to be changed.
            field = rule['FeatureName'] = table[i+1][sfoo.index('FeatureName')]

            # Get source (original) and target (new) feature values.
            field = rule['Rules'] = table[i+1][sfoo.index('Rules')]
            pairs = field.split(',')
            assert pairs[-1] == ''
            pairs = pairs[:-1]
            assert all(len(p) == 2 for p in pairs)
            field = [[p[0], p[1]] for p in pairs]
            rule['Rules'] = field

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

                if i != 0 and fieldname == 'Rules':
                    field = ','.join([''.join([p[0], p[1]]) for p in field])
                    field += ','

                # Add field value to output.
                result[-1].append(field)

        return result

#==============================================================================
