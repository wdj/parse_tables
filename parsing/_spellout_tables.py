#!/usr/bin/env python3
"""============================================================================

Tools for tables that appear in dialog boxes for spellout-like rules.
(Note this is different from database tables in .mdb files)

The relevant string has three parts:
1. Head matter, such as structures or features that apply to all rows
   of the table.
2. Table number of rows and columns, followed by a series of row descriptors,
   each with info such as row name and structures / features applying to the
   row.
3. Similar info for columns, then the actual table entries themselves.

Syntax can vary slightly based on rule_type (wihch of the several spellout
rule based tables) and the the rule (sub) type of the spellout rule variant.

============================================================================"""

import sys
import re

import _utils
from _input_structures import *
from _output_structures import *

#------------------------------------------------------------------------------

def import_spellout_table(in_: str, rule_type: int, rule_subtype: int) -> list:
    """Import a table associated with a spellout-type rule."""

    out = []

    if in_ == '':
        return out

    is_pb = rule_subtype == _utils.SPELLOUT_RULE_TYPES['Phrase Builder']
    is_table = rule_subtype == _utils.SPELLOUT_RULE_TYPES['Table']

    parts = in_.split('>|<')

    # First part: layer title and general features.

    if is_pb:

        table_name, info = parts[0].split('|', 1)

        structures = info.split('^~^')
        assert len(structures) <= 2

        if len(structures) >= 1:
            structures[0] = import_input_structures(structures[0], rule_type)

        if len(structures) >= 2:
            structures[1] = import_output_structures(structures[1], rule_type)

        out.append([table_name, structures])

    elif is_table:

        table_name, info = parts[0].split('|', 1)

        features = info.split('^')
        assert features == [''] or len(features) in [1, 3]

        out.append([table_name, features])

    else: # is_suppletive

        word_id = parts[0]

        out.append([word_id, ''])

    # Middle parts: table dimensions and row descriptors.

    num_row, num_col = parts[1].split('|',2)[:2]
    assert num_row.isdigit()
    assert num_col.isdigit()
    out.append([num_row, num_col])

    if is_table:

        assert len(parts) == 2

        part1 = parts[1].split('|', 2+int(num_row))

        parts = [parts[0], '|'.join(part1[:3])] + part1[3:]

    for i, row_info in enumerate(parts[1:-1]):

        row_tmp = str(row_info)

        if i == 0:
            _, _, row_tmp = row_tmp.split('|',2)

        if row_tmp == '':
            out.append(['', ''])
            # Table has no row info, so just continue.
            continue

        row_name, info = row_tmp.split('@', 1)

        if is_pb:

            structures = info.split('^~^')
            assert len(structures) <= 2

            if len(structures) >= 1:
                structures[0] = import_input_structures(structures[0],
                                                        rule_type)

            if len(structures) >= 2:
                structures[1] = import_output_structures(structures[1],
                                                         rule_type)

            out.append([row_name, structures])

        else: # is_suppletive

            features = info.split('^')
            assert len(features) == (1
                if rule_type == _utils.RULE_TYPES['Rules_Lexical'] else 3)

            out.append([row_name, features])

    # Last part: column widths, column descriptors and table elements.

    num_row, num_col = int(num_row), int(num_col)

    row_tmp = str(parts[-1])

    col1_width, row_tmp = row_tmp.split('|', 1)
    col_widths = [col1_width]

    row_tmp = row_tmp.split('|', 2*num_col)

    table_entries, table_entry_comments = (
        row_tmp[-1].split('~!~') + [''])[:2]

    table_entries = table_entries.split('|')
    del table_entries[-1] # account for trailing delimiter.
    assert len(table_entries) == num_row * num_col

    table_entry_comments = table_entry_comments.split('^')
    assert table_entry_comments == [''] or (
        len(table_entry_comments) == num_row * num_col + 1)

    col_names, col_features = [], []

    for i in range(num_col):

        # Note ignoring final list item (table_entries)
        col_width = row_tmp[2*i]
        col_name, col_features_this = (row_tmp[2*i+1] + '@').split('@')[:2]

        col_widths.append(col_width)
        col_names.append(col_name)
        col_features.append(col_features_this)

    out.append([col_widths, col_names, col_features,
                table_entries, table_entry_comments])

    return out

#------------------------------------------------------------------------------

def import_spellout_tables(in_: str, rule_type: int, rule_subtype: int) -> list:
    """Do import_spellout_table for a string with muliple tables."""

    out = [import_spellout_table(layer, rule_type, rule_subtype)
           for layer in in_.split('~!!~')]

    return out

#------------------------------------------------------------------------------

def export_spellout_table(in_: list, rule_type: int, rule_subtype: int) -> str:
    """Export a table associated with a spellout-type rule."""

    out = ''

    if in_ == []:
        return out

    is_pb = rule_subtype == _utils.SPELLOUT_RULE_TYPES['Phrase Builder']
    is_table = rule_subtype == _utils.SPELLOUT_RULE_TYPES['Table']

    # First part: layer title and general features.

    name, info = in_[0]

    if is_pb:

        out += name + '|'

        structures = info

        out += export_input_structures(structures[0], rule_type)
        if len(structures) >= 2 and structures[1] != []:
            out += '^~^'
            out += export_output_structures(structures[1], rule_type)

    elif is_table:

        out += name + '|'

        features = info

        out += '^'.join(features)

    else:

        out += name

    out += '>|<'

    # Middle parts: table dimensions and row descriptors.

    num_row, num_col = in_[1]

    out += num_row + '|' + num_col + '|'

    for part in in_[2:-1]:

        name, info = tuple(part)

        out += name

        if is_pb:

            out += '@' if name != '' else ''

            structures = info

            out += export_input_structures(structures[0], rule_type)
            if len(structures) >= 2 and structures[1] != []:
                out += '^~^'
                out += export_output_structures(structures[1], rule_type)

            out += '>|<'

        elif is_table:

            features = info

            out += '@' if name != '' or (
                rule_type == _utils.RULE_TYPES['Rules_Lexical'] and
                name + '^'.join(features) != '') else ''

            out += '^'.join(features)

            out += '|'

        else:

            features = info

            out += '@' if name != '' or (
                rule_type == _utils.RULE_TYPES['Rules_Lexical'] and
                name + '^'.join(features) != '') else ''

            out += '^'.join(features)

            out += '>|<'

    # Last part: column widths, column descriptors and table elements.

    col_widths, col_names, col_features, table_entries, table_entry_comments = (
        in_[-1])

    out += col_widths[0] + '|'

    for i in range(len(col_names)):
        out += col_widths[1+i] + '|'
        out += col_names[i] + '@' if col_names[i] != '' else ''
        out += col_features[i] + '|'

    for i in range(len(table_entries)):
        out += table_entries[i] + '|'

    if table_entry_comments != ['']:
        out += '~!~'
        out += '^'.join(table_entry_comments)

    return out

#------------------------------------------------------------------------------

def export_spellout_tables(in_: list, rule_type: int, rule_subtype: int) -> str:
    """Do export_spellout_table for a string with muliple tables."""

    out = '~!!~'.join(export_spellout_table(layer, rule_type, rule_subtype)
                       for layer in in_)

    return out

#------------------------------------------------------------------------------




