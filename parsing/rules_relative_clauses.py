#!/usr/bin/env python3
"""============================================================================

Handle Rules_RelativeClauses table from <MyLanguage>.mdb file.

============================================================================"""

import re

import _utils

#==============================================================================

class RulesRelativeClauses:
    """
    Handle Rules_RelativeClauses table from <MyLanguage>.mdb file.

    -----------------------------------------------------------------------
    Notes

    see CExecuteRules::ExecuteRelativeClauseStrategies
    see CTA1Doc::GetRelativeClauseRule
    see CTA1Doc::GetRelativeClauseStructure

    Structure is six characters:
    1: the embedded/adjoined flag. 0=embedded, 1=adjoined
    2: the nominal position flag. 0=prenominal, 1=postnominal, 2=circumnominal
    3: the sentence initial or final flag for adjoined RCs.
    4-6: sentence initial or final position (chars 4-6 cast to int (?))
    4: the circum-nominal's head character
    5: the trace character for restrictive relative clauses
       (if "", " " or ".", use ".")
    6: the trace character for descriptive relative clauses
       (if "", " " or ".", use ".")
    if empty, default to "000" - embedded, prenominal, sentence initial

    Strategies is two characters:
    1: strategy
    2: relativizer flag

    Features is a (comma-separated) features string (no syncat char).
    It is for matching the noun phrase.

    Relativizer is the word, if any, that sets off the rel clause.

    -----------------------------------------------------------------------
    """

    RULE_TYPE = _utils.RULE_TYPES['Rules_RelativeClauses']

    # List of fields that are needed for the translation/generation.

    FIELDNAMES_IMPT = [
        'Strategies',
        'Relativizer',
        'Features',
        'Structure',
    ]

    # Define all fields associated wtih this table.

    FIELDNAMES = [
        'ID', # it would seem this not needed for translation
        'Comment',
        'CommentFonts',
        'References',
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

            # Get the relativization strategy.
            field = rule['Strategies'] = table[i+1][sfoo.index('Strategies')]
            assert len(field) == 2

            # Get the relativizer word.
            field = rule['Relativizer'] = table[i+1][sfoo.index('Relativizer')]

            # Get the features that must be matched by the noun phrase.
            field = rule['Features'] = table[i+1][sfoo.index('Features')]

            # Get the structure for how the rel clause is built.
            field = rule['Structure'] = table[i+1][sfoo.index('Structure')]
            assert len(field) >= 6 or field == ''

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

                # ...

                # Add field value to output.
                result[-1].append(field)

        return result

#==============================================================================
