#!/usr/bin/env python3
"""============================================================================

Handle Rules_Clitic table from <MyLanguage>.mdb file.

============================================================================"""

import re

import _utils
from _input_structures import *

#==============================================================================

class RulesClitic:
    """
    Handle Rules_Clitic table from <MyLanguage>.mdb file.

    -----------------------------------------------------------------------
    Notes

    To understand this rule better, see the following:

    The Rules_Clitic table in English.mdb (or other lang) will show the
    fieldnames (see code below) and examples.

    TA1Doc.cpp, lines 18803f (CTA1Doc::GetRule) shows how each rule in the
    table is encoded into a single string: roughly,
    strGroupName +CR+
    status + CR +
    strClitic +CR+
    strTag +CR+
    strFeatures +CR+
    strInputStructure +CR+
    clitic type +
    clitic attaches

    (somewhere in between, the group name is stripped off the front of the
    string)

    ExecuteRules.cpp, lines 15866f (ExecuteRules::ExecuteRule) shows how
    this is parsed.

    CheckFeatures checks for eature match. if not, then return

    LoadInputStructure parses the structure pattern

    WARNING: LoadInputStructure has some inline comments that don't
    exactly fit, e.g., a "word" can actually be a parenthesis. A better
    term might be "token".

    CheckInputStructure checks for structure match.

    NOTE: for the clitics case, the input structure assumes:
    m_bIgnorePhrasalEmbedding = FALSE;
    m_bIgnoreClausalEmbedding = FALSE;

    -----------------------------------------------------------------------
    """

    RULE_TYPE = _utils.RULE_TYPES['Rules_Clitic']

    # List of fields that are needed for the translation/generation.

    FIELDNAMES_IMPT = [
        'Status',
        'SyntacticCategory',
        'CliticType',
        'Features',
        'InputStructure',
        'Clitic',
        'CliticAttaches',
    ]

    # Define all fields associated wtih this table.

    FIELDNAMES = [
        'ID', # it would seem this not needed for translation
        'GroupName', # ??? is this needed for the translation
        'RulesName', # this is human-readable, seems not needed for translation
        'Tag',
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

            # Where is the clitic placed with respect to the word.
            field = rule['CliticType'] = table[i+1][sfoo.index('CliticType')]
            assert field in _utils.CLITIC_TYPES

            # Specify features for match. Delimiter is "^"; 3 fields:
            # word features, phrase features, clause features.
            field = rule['Features'] = (
                table[i+1][sfoo.index('Features')].split('^'))

            # Parse the input structure.
            field = rule['InputStructure'] = import_input_structure(
                table[i+1][sfoo.index('InputStructure')],
                rule_type=self.RULE_TYPE)

            # Get the clitic letters/punctuation (single, or tabular)
            field = rule['Clitic'] = table[i+1][sfoo.index('Clitic')]
            assert '<|>' not in rule['Clitic'], (
                "Error: tabular form of clitic rule not implemented.")
            # TODO: implement tabular case, cf. CliticRuleDlg.cpp.

            # Does the clitic attach to the word.
            field = rule['CliticAttaches'] = (
                table[i+1][sfoo.index('CliticAttaches')])
            assert field in ['0', '1']

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

                if i != 0 and fieldname == 'InputStructure':
                    field = export_input_structure(field, 
                                                   rule_type=self.RULE_TYPE)

                if i != 0 and fieldname == 'Features':
                    field = '^'.join(field)

                # Add field value to output.
                result[-1].append(field)

        return result

#==============================================================================
