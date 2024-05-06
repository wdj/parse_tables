#!/usr/bin/env python3
"""============================================================================

Handle Rules_FeatureCopying table from <MyLanguage>.mdb file.

============================================================================"""

import re

import _utils
from _input_structures import *
from _output_structures import *

#==============================================================================

class RulesFeatureCopying:
    """
    Handle Rules_FeatureCopying table from <MyLanguage>.mdb file.

    -----------------------------------------------------------------------
    Notes

    see CExecuteRules::CopyFeatures
    see CTA1Doc::GetFeatureCopyingRule
    see CTA1Doc::GetCopiedFeature
    see CTA1Doc::GetCopiedFeatureInfo
    see CAgreementRuleDlg::LoadFeatures

    TypeOfRule: 0 = feature copying rule, 1 = feature setting rule

    SourceSyntacticCategory: syncat of where feature being copied 'from"
      however if feature setting rule then "0"

    Structure:
      table of subrules, delimited by >|< (and at end)
      if TypeOfRule is 0 each table entry is prepended with
      i**j** where i is the 0-based line of the source and
      j is the 0-based line of the destination
      if TypeOfRule is 1 then functions very much like InputStructures
      for copying features.

      It would seem that for each structure, all of the SourceFeature
      fileds of the given table row are copied.

    OutputStructures:
      table of subrules, delimited by >|< (and at end)
      if TypeOfRule is 0 then null str
      if TypeOfRule is 1 then functions very much like (usual)
      OutputStructures for copying features.

    DefaultValue: one table entry (delimiter "^", one at end) per
      feature copied.
      The idea seems top be this. the target word (always) acquires
      this new feature name because of this rule, but it needs to have a
      default value in case there is no source word requiring agreement.
      this setting defines this.
      however if feature setting rule then DefaultValue is null str

    DefaultCharacters: one character per feature copied.
      if Source Unavailable, then for that slot is "-"
      however if feature setting rule then DefaultCharacters is null str

    -----------------------------------------------------------------------
    """

    RULE_TYPE = _utils.RULE_TYPES['Rules_FeatureCopying']

    # List of fields that are needed for the translation/generation.

    FIELDNAMES_IMPT = [
        'Status',
        'SyntacticCategory', # this is the DESTINATION syncat
        'SourceSyntacticCategory',
        'NewName', # name/s of source feature/s, renamed for DESTINATION
        'SourceFeature',
        'Structure',
        'OutputStructures',
        'DefaultValue',
        'DefaultCharacters',
        'TypeOfRule', # feature copying or feature setting
    ]

    # Define all fields associated wtih this table.

    FIELDNAMES = [
        'ID', # it would seem this not needed for translation
        'Comment',
        'CommentFonts',
        'References',
        'NameFonts',
        'GrammarTopics',
        'ColumnWidth',
        'GroupName', # ??? is this needed for the translation
        'RulesName', # this is human-readable, seems not needed for translation
        'Source', # seems always "0", never acessed from table
        'Destination', # seems always "0", never acessed from table
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

            # Feature copying = 0, feature setting = 1
            field = rule['TypeOfRule'] = (
                table[i+1][sfoo.index('TypeOfRule')])
            assert field in ['0', '1']
            type_of_rule = str(field)
            is_copying = type_of_rule == '0'

            # What is the syncat of the destination word.
            field = rule['SyntacticCategory'] = (
                table[i+1][sfoo.index('SyntacticCategory')])
            # ISSUE: the following could possibly be made more restrictive.
            # ISSUE: does this need to account for user-defined syncats.
            assert field in _utils.SYNTACTIC_CATEGORIES.values()

            # What is the syncat of the source word.
            field = rule['SourceSyntacticCategory'] = (
                table[i+1][sfoo.index('SourceSyntacticCategory')])
            # ISSUE: the following could possibly be made more restrictive.
            # ISSUE: does this need to account for user-defined syncats.
            assert field in _utils.SYNTACTIC_CATEGORIES.values() if (
                is_copying) else '0'

            # Parse the input structure.
            field = table[i+1][sfoo.index('Structure')]
            num_structures = len(field.split('>|<')[:-1])
            assert num_structures >= 1 or not is_copying
            field = rule['Structure'] = import_input_structures(
                field, rule_type=self.RULE_TYPE)

            # Parse the output structure.
            field = table[i+1][sfoo.index('OutputStructures')]
            assert field == '' or not is_copying
            assert len(field.split('>|<')[:-1]) == num_structures or (
               is_copying)
            field = rule['OutputStructures'] = import_input_structures(
                field, rule_type=self.RULE_TYPE) if not is_copying else ''

            # Set the name of the feature to be copied or set.
            field = rule['SourceFeature'] = (
                table[i+1][sfoo.index('SourceFeature')])
            num_copied_features = len(field.split('^')[:-1]) if (
              is_copying) else 0
            assert field == '' or is_copying
            assert len(field.split('^')[:-1]) == num_copied_features or (
                not is_copying)

            # Set the new name of the copied feature.
            field = rule['NewName'] = (
                table[i+1][sfoo.index('NewName')])
            assert field == '' or is_copying
            assert len(field.split('^')[:-1]) == num_copied_features or (
                not is_copying)

            # Default value of new feature if otherwise unavailable.
            field = rule['DefaultValue'] = (
                table[i+1][sfoo.index('DefaultValue')])
            assert field == '' or is_copying
            assert len(field.split('^')[:-1]) == num_copied_features or (
                not is_copying)

            # Single-character identifiers of defaults.
            field = rule['DefaultCharacters'] = (
                table[i+1][sfoo.index('DefaultCharacters')])
            assert field == '' or is_copying
            assert len(field) == num_copied_features or (
                not is_copying)

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
            type_of_rule = '' if i == 0 else self._rules[i-1]['TypeOfRule']
            for j in range(len(self._fieldnames_order_orig)):
                k = self.FIELDNAMES.index(self._fieldnames_order_orig[j])
                fieldname = self.FIELDNAMES[k]

                # Pick up field from either the header or the rule.
                field = fieldname if i==0 else self._rules[i-1][fieldname]

                # Correct entries that have had special parsing.

                if i != 0 and fieldname == 'Structure':
                    field = export_input_structures(field, 
                                                    rule_type=self.RULE_TYPE)
                if i != 0 and fieldname == 'OutputStructures':
                    field = export_input_structures(field, 
                      rule_type=self.RULE_TYPE) if type_of_rule == '1' else ''

                # Add field value to output.
                result[-1].append(field)

        return result

#==============================================================================
