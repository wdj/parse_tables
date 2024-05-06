#!/usr/bin/env python3
"""============================================================================

Handle Rules_SpeechStyles table from <MyLanguage>.mdb file.

============================================================================"""

import re

import _utils

#==============================================================================

class RulesSpeechStyles:
    """
    Handle Rules_SpeechStyles table from <MyLanguage>.mdb file.

    -----------------------------------------------------------------------
    Notes

    see CExecuteRules::ExecuteSpeechStyleRules
    see CTA1Doc::GetSpeechStylesRule

    InputFeatures has four fields, delimited by "^"
    the first three are features for the relevant verb, verb phrase and
    clause.
    If no verb, then first two fields are null string.
    Fourth field is "source text" (?)
    OutputFeatures is a comma-separated list of features that are
    apparently prepended to the verb feature list if there is a match.

    -----------------------------------------------------------------------
    """

    RULE_TYPE = _utils.RULE_TYPES['Rules_SpeechStyles']

    # List of fields that are needed for the translation/generation.

    FIELDNAMES_IMPT = [
        'Status',
        'InputFeatures',
        'OutputFeatures',
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

            # Is the rule set to "active" (to be used when translating).
            field = rule['Status'] = table[i+1][sfoo.index('Status')]
            assert field in ['0', '1']

            # Input features string.
            field = rule['InputFeatures'] = (
                table[i+1][sfoo.index('InputFeatures')])
            field = field.split('^')
            rule['InputFeatures'] = field
            assert len(field) == (4 if
              self.RULE_TYPE == _utils.RULE_TYPES['Rules_SpeechStyles'] else 3)

            # Output features string.
            field = rule['OutputFeatures'] = (
                table[i+1][sfoo.index('OutputFeatures')])
            field = field.split(',')
            rule['OutputFeatures'] = field

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

                if i != 0 and fieldname == 'InputFeatures':
                    field = '^'.join(field)

                if i != 0 and fieldname == 'OutputFeatures':
                    field = ','.join(field)

                # Add field value to output.
                result[-1].append(field)

        return result

#==============================================================================
