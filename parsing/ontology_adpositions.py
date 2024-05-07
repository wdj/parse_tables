#!/usr/bin/env python3
"""============================================================================

Handle Adpositions table from Ontology.mdb file.

============================================================================"""

import _utils

#==============================================================================

class OntologyAdpositions:
    """
    Handle Adpositions table from Ontology.mdb file.
    """

    RULE_TYPE = _utils.RULE_TYPES['Ontology_Adpositions']

    # List of fields that are needed for the translation/generation.

    FIELDNAMES_IMPT = [
        'Roots',
        'Categories',
        'Level',
        'ParentID',
    ]

    # Define all fields associated wtih this table.

    FIELDNAMES = [
        'ID', # Need only in order to sort records into proper order.
        'Glosses',
        'Occurrences',
        'Comments',
        'LN Base',
        'LN Sense',
        'LN Gloss',
        'LN Definition',
        'LN Note',
        'LN Tag',
        'Examples',
        'Exhaustive Examples',
        'Expansion Rule',
        'Expansion Rule Status',
        'Brief Gloss',
        'Linguists Assistant',
    ] + FIELDNAMES_IMPT

#------------------------------------------------------------------------------

    def __init__(self):
        """Constructor for class."""

        self._is_set = False
        self._fieldnames = list(self.FIELDNAMES)
        self._fieldnames_impt = list(self.FIELDNAMES_IMPT)
        self._perm = None
        self._iperm = None

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
                if fieldname not in self._fieldnames_impt:
                    j = sfoo.index(fieldname)
                    rule[fieldname] = table[i+1][j]

            # Roots.
            field = rule['Roots'] = table[i+1][sfoo.index('Roots')]

            # Categories.
            field = rule['Categories'] = table[i+1][sfoo.index('Categories')]

            # Level (sematic atom, etc.).
            field = rule['Level'] = table[i+1][sfoo.index('Level')]

            # ParentID
            field = rule['ParentID'] = table[i+1][sfoo.index('ParentID')]

            # Generic Thing-Thing Relationships.
            if 'Generic Thing-Thing Relationships' in self._fieldnames_impt:
                field = rule['Generic Thing-Thing Relationships'] = (
                    table[i+1][sfoo.index('Generic Thing-Thing Relationships')])

            self._rules.append(rule)

        # Finally, sort to be in proper order (ascending order in key "ID").
        # First compute permutation vector and its inverse.

        self._perm = [i for _, i in sorted(zip(self._rules, list(range(len(self._rules)))), key = lambda row: row[0]['ID'])]
       
        self._iperm = [0] * len(self._rules) 
        [self._iperm.__setitem__(p, i) for i, p in enumerate(self._perm)]

        self._rules = sorted(self._rules, key = lambda row: row['ID'])

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
                field = fieldname if i==0 else self._rules[
                                                self._iperm[i-1]][fieldname]

                # Correct entries that have had special parsing.

                # N/A

                # Add field value to output.
                result[-1].append(field)

        return result

#==============================================================================



