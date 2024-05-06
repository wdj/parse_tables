#!/usr/bin/env python3
"""============================================================================

Handle Nouns table from <MyLanguage>.mdb file.

============================================================================"""

import re

import _utils

#==============================================================================

class Nouns:
    """
    Handle Nouns table from <MyLanguage>.mdb file.

    -----------------------------------------------------------------------
    Notes


    -----------------------------------------------------------------------
    """

    RULE_TYPE = _utils.RULE_TYPES['Nouns']

    # List of fields that are needed for the translation/generation.

    FIELDNAMES_IMPT = [
        'Roots',
        'Features',
        'Constituents',
        'EntryID',
    ]

    # Define all fields associated wtih this table.

    FIELDNAMES = [
        'ID', # it would seem this not needed for translation
        'Comments',
        'GlossFonts',
        'CommentFonts',
        'Glosses',
        'VocabularyQuizzerTarget',
        'VocabularyQuizzerGloss',
        'VocabularyQuizzerDifficultTarget',
        'VocabularyQuizzerDifficultGloss',
        'AudioFile',
        'AudioFileTargetText',
        'AudioFileEnglishText',
        'VocabularyQuizzerAudio',
        'VocabularyQuizzerDifficultAudio',
        'SampleSentences',
        'SemanticDomains',
        'UserDefinedFields',
        'RelatedLanguageStems',
        'Spare 2',
        'Spare 3',
        'Spare 4',
        'Spare 5',
        'DeepForms',
        'FormReferences',
    ] + FIELDNAMES_IMPT

#------------------------------------------------------------------------------

    def __init__(self):
        """Constructor for class."""

        self._is_set = False
        self._fieldnames = list(self.FIELDNAMES)

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
        # Make correction for some cases.
        for fieldname in ['Spare 2', 'Spare 3', 'FormReferences']:
            if fieldname in self._fieldnames and (
                fieldname not in table_header):
                self._fieldnames.remove(fieldname)
        for fieldname in ['Form 1', 'Form 2']:
            if fieldname in table_header and (
                fieldname not in self._fieldnames):
                self._fieldnames.append(fieldname)
        # Check table header (field names) correctness.
        if len(table_header) != len(self._fieldnames):
            print(1, [a for a in table_header if a not in self._fieldnames])
            print(2, [a for a in self._fieldnames if a not in table_header])
        assert len(table_header) == len(self._fieldnames)
        # Are all fields present, even if in different order.
        assert set(table_header) == set(self._fieldnames)

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
            for fieldname in self._fieldnames:
                if fieldname not in self.FIELDNAMES_IMPT:
                    j = sfoo.index(fieldname)
                    rule[fieldname] = table[i+1][j]

            # Roots.
            field = rule['Roots'] = table[i+1][sfoo.index('Roots')]

            # Features.
            field = rule['Features'] = table[i+1][sfoo.index('Features')]

            # Constituents
            field = rule['Constituents'] = table[i+1][sfoo.index(
                         'Constituents')]

            # EntryID.
            field = rule['EntryID'] = table[i+1][sfoo.index('EntryID')]

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
                k = self._fieldnames.index(self._fieldnames_order_orig[j])
                fieldname = self._fieldnames[k]

                # Pick up field from either the header or the rule.
                field = fieldname if i==0 else self._rules[i-1][fieldname]

                # Correct entries that have had special parsing.

                # N/A

                # Add field value to output.
                result[-1].append(field)

        return result

#==============================================================================
