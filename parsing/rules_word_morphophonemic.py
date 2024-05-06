#!/usr/bin/env python3
"""============================================================================

Handle Rules_WordMorphophonemic table from <MyLanguage>.mdb file.

============================================================================"""

import re

import _utils

#==============================================================================

class RulesWordMorphophonemic:
    """
    Handle Rules_WordMorphophonemic table from <MyLanguage>.mdb file.

    -----------------------------------------------------------------------
    Notes

see
ExecuteRules.cpp, lines 14827f


    -----------------------------------------------------------------------
    """

    RULE_TYPE = _utils.RULE_TYPES['Rules_WordMorphophonemic']

    # List of fields that are needed for the translation/generation.

    FIELDNAMES_IMPT = [
        'Status',
        'SyntacticCategory',
        'TriggerWord',
        'Input',
        'Output',
        'Features',
        'EnvironmentLocation',
        'EnvironmentFeatures',
        'PhoneticFeatures',
        'ExcludedWords',
        'ExcludedMorphemes',
        'UserDefinedSyntacticCategory',
    ]

    # Define all fields associated wtih this table.

    FIELDNAMES = [
        'ID', # it would seem this not needed for translation
        'GroupName', # ??? is this needed for the translation
        'RulesName', # this is human-readable, seems not needed for translation
        'Comment',
        'CommentFonts',
        'NameFonts',
        'References',
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

            # Word to be modified. Either word number or, if user
            # defined syncat, the word itself. Comma-separated (apparently).
            # if first chracter of this field is "." then "excluded"
            # (invert the search, but apparently stay in this syncat)
            field = rule['TriggerWord'] = table[i+1][sfoo.index(
                         'TriggerWord')]
            rule['TriggerWord'] = (
                [True] + field[1:].split(',')) if (
                field != '' and field[0] == '.') else (
                [False] + field.split(','))

            # Affected word's input features or characters
            # Note: if last letter of Input or Output is "^",
            # then this is a phoneme string.
            # ISSUE: in this case, what does it mean for the
            # output word or environment change to changed into phonemes.
            field = rule['Input'] = table[i+1][sfoo.index(
                         'Input')]

            # Affected word's output features or characters
            field = rule['Output'] = table[i+1][sfoo.index(
                         'Output')]

            # Match string pertaining to trigger word and containing
            # phrase and clause. Could be blank or one or three feature
            # values strings joined by "^".
            field = rule['Features'] = table[i+1][sfoo.index(
                         'Features')].split('^')

            # "0" = preceding the word, "1" = following the word
            field = rule['EnvironmentLocation'] = table[i+1][sfoo.index(
                         'EnvironmentLocation')]
            assert field in ["0", "1"]

            # A match specification for environment.
            # if first char is "&", then user defined syncat
            # else standard syncat id, then "-", then feature string.
            field = rule['EnvironmentFeatures'] = table[i+1][sfoo.index(
                         'EnvironmentFeatures')]
            rule['EnvironmentFeatures'] = [] if field == '' else (
                [True] + [field[1:]]) if (
                field != '' and field[0] == '&') else (
                [False] + [field.split('-',1)[0]]
                        + field.split('-',1)[1].split('^'))

            # The following refers to the environment word.
            # first char: 0=phonetic features, 1=alphabetic chars
            # phonetic case: five "^"-followed phoneme specifiers
            # (each a comma separated and terminated list of phoneme types),
            # optionally followed by spec of how the environment word
            # is to change.
            # alpha case: either a string (match string), or two strings
            # separated by "^" (match string and change string).
            # match string is list of "|"-delimited substrings
            # Note "#" can be used to denote a word boundary.
            # change string seems to have similar format.
            # TODO: figure this out better; parse.

            field = rule['PhoneticFeatures'] = table[i+1][sfoo.index(
                         'PhoneticFeatures')]

            # List of excluded environment words and their syncats.
            # First char = "." if excluded, otherwise included.
            # Perhaps named such because the typical use case is to exclude.
            # Dialog name is "Environment Words".
            field = rule['ExcludedWords'] = table[i+1][sfoo.index(
                         'ExcludedWords')]
            rule['ExcludedWords'] = (
                [True] + field[1:].split(',')) if (
                field != '' and field[0] == '.') else (
                [False] + field.split(','))

            # "|"-separated tags, defined upstream, to be excluded when
            # seeking to match the environment.
            field = rule['ExcludedMorphemes'] = table[i+1][sfoo.index(
                         'ExcludedMorphemes')].split('|')

            # If SyntacticCategory is 106 (user defined), this field
            # specifies exactly which user defined syncat it is.
            field = rule['UserDefinedSyntacticCategory'] = (
                    table[i+1][sfoo.index(
                         'UserDefinedSyntacticCategory')])





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

                if i != 0 and fieldname == 'TriggerWord':
                    field = '.' + ','.join(field[1:]) if field[0] else (
                        ','.join(field[1:]))

                if i != 0 and fieldname == 'Features':
                    field = '^'.join(field)

                if i != 0 and fieldname == 'EnvironmentFeatures':
                    field = '' if field == [] else (
                            '&' + field[1]) if field[0] else (
                            field[1] + '-' + '^'.join(field[2:]))

                if i != 0 and fieldname == 'ExcludedWords':
                    field = '.' + ','.join(field[1:]) if field[0] else (
                        ','.join(field[1:]))

                if i != 0 and fieldname == 'ExcludedMorphemes':
                    field = '|'.join(field)

                # Add field value to output.
                result[-1].append(field)

        return result

#==============================================================================
