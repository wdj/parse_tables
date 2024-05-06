#!/usr/bin/env python3
"""============================================================================

Handle Rules_Transfer table from <MyLanguage>.mdb file.

============================================================================"""

import re

import _utils
from _input_structures import *
from _output_structures import *

#==============================================================================

class RulesTransfer:
    """
    Handle Rules_Transfer table from <MyLanguage>.mdb file.

    -----------------------------------------------------------------------
    Notes


    -----------------------------------------------------------------------
    """

    RULE_TYPE = _utils.RULE_TYPES['Rules_Transfer'] # CHECK

    # List of fields that are needed for the translation/generation.

    FIELDNAMES_IMPT = [
        'SyntacticCategory',
        'Status',
        'InputStructures',
        'OutputStructures',
        'TriggerWord',
        'SourceLanguage',
        'UserDefinedInsertions',
        'IgnorePhrasalEmbedding',
        'IgnoreClausalEmbedding',
        'IncludePreviousVerse',
        'ContinueExecution',
        'SSDS', # same subject different subject # stores nominal indices
    ]

    # Define all fields associated wtih this table.

    FIELDNAMES = [
        'ID', # it would seem this not needed for translation - CHECK
        'GroupName', # ??? is this needed for the translation
        'RulesName', # this is human-readable, seems not needed for translation
        'Comment',
        'CommentFonts',
        'NameFonts',
        'References',
        'GrammarTopics',
    ] + FIELDNAMES_IMPT

#------------------------------------------------------------------------------

    # TODO: eventually will need to be able to update all rules if
    # something fundamental is changed like modify/delete word in
    # lexicon or add/remove/modify features or feature values.

    def __init__(self):
        """Constructor for class."""

        self._is_set = False

#------------------------------------------------------------------------------

    def import_table(self, table: list):
        """
        Import and parse the table.
        The input is a list of rows, each row is a list of fields.

        CHECK:
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

            # Parse the input structures.
            field = rule['InputStructures'] = import_input_structures(
                table[i+1][sfoo.index('InputStructures')],
                rule_type=self.RULE_TYPE)

            # Parse the output structures.
            field = rule['OutputStructures'] = import_output_structures(
                table[i+1][sfoo.index('OutputStructures')],
                rule_type=self.RULE_TYPE)
            assert len(rule['InputStructures']) == len(rule['OutputStructures'])

            # It appears this, from the ontology not the TL, is set based on
            # the syncat of the rule and SL word/s matching this in the
            # InputStructures. It can be multiple, comma-separated.
            # The last one always followed by a comma.
            field = rule['TriggerWord'] = (
                table[i+1][sfoo.index('TriggerWord')])

            field = rule['SourceLanguage'] = (
                table[i+1][sfoo.index('SourceLanguage')])
            # "-1=no source, 0=Hebrew, 1=Greek[, 2=English]"
            assert field in ['-1', '0', '1', '2']

            # This it seems is occurrences of user-defined syncats in the rule,
            # separated by crlf. Each has 3 fields: the user defined syncat,
            # the syncat number of the constituent it occurs in, and the
            # user defined syncat word; these are delimited by "~!~"
            field = rule['UserDefinedInsertions'] = (
                table[i+1][sfoo.index('UserDefinedInsertions')])

            # This is a bitstring, stored as a string, 0 or 1 for each subrule.
            # though can be more general - see ExecuteRules.cpp, line 13024
            # the value is true if the string is at least as long as the
            # structure and the corresponsing entry is "1" else false.
            # (similarly below)
            field = rule['IgnorePhrasalEmbedding'] = (
                table[i+1][sfoo.index('IgnorePhrasalEmbedding')])
            assert all(c in {'0', '1', 'N', 'o'} for c in field)

            # This is a bitstring, stored as a string, 0 or 1 for each subrule.
            field = rule['IgnoreClausalEmbedding'] = (
                table[i+1][sfoo.index('IgnoreClausalEmbedding')])
            #assert all(c in {'0', '1'} for c in field)
            assert all(c in {'0', '1', 'N', 'o'} for c in field)

            field = rule['IncludePreviousVerse'] = (
                table[i+1][sfoo.index('IncludePreviousVerse')])
            assert field in ['0', '1']

            # This is a bitstring, stored as a string, 0 or 1 for each subrule.
            field = rule['ContinueExecution'] = (
                table[i+1][sfoo.index('ContinueExecution')])
            assert all(c in {'0', '1', 'N', 'o'} for c in field)

            # This is for each subrule, delimited by "-*-" (this also at
            # the end of the string). For a given subrule, a series of
            # digits in the range 0-9, corresponding to the nouns in the
            # InputStructure, denoting the nominal index of the noun.
            # Apparently defaults to "0" for all nouns. Empty string if
            # no nouns.
            field = table[i+1][sfoo.index('SSDS')]
            assert all(c in set('0123456789-*') for c in field)
            field = rule['SSDS'] = field.split('-*-')

            # Add rule to list.
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
            # Loop over fields.
            for j in range(len(self._fieldnames_order_orig)):
                k = self.FIELDNAMES.index(self._fieldnames_order_orig[j])
                fieldname = self.FIELDNAMES[k]

                # Pick up field from either the header or the rule.
                field = fieldname if i==0 else self._rules[i-1][fieldname]

                # Correct entries that have had special parsing.

                if i != 0 and fieldname == 'InputStructures':
                    field = export_input_structures(field,
                                                    rule_type=self.RULE_TYPE)

                if i != 0 and fieldname == 'OutputStructures':
                    field = export_output_structures(field,
                                                     rule_type=self.RULE_TYPE)

                if i != 0 and fieldname == 'SSDS':

                    #field = '' if field == [] else '-*-'.join(field) + '-*-'
                    field = '-*-'.join(field)

                # Add field value to output.
                result[-1].append(field)

        return result

#==============================================================================
