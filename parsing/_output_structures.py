#!/usr/bin/env python3
"""============================================================================

Tools for OutputStructure and OutputStructures tables.

The OutputStructure/s strings are similar to the corresponding InputStructure/s
strings. Each line however generally has four tokens.

For a few rule types (table types) such as the spellout rule tables, each line
of the string is much more minimal.

============================================================================"""

import sys
import re

import _utils

#------------------------------------------------------------------------------

def import_output_structure(in_: str, rule_type: int) -> list:
    """This code reproduces the behavior of CExecuteRules::LoadOutputStructure
       and other functions.

       The syntax very much resembles that of InputStructure, with the
       following differences:

- There is now a fourth field, it is "1" if the line is one of the two forms of "Insert" or "Copy" or "CopyPhrase", 0 otherwise. Also occasionally "1" is the fourth field of open and close of a phrase for which a word has been inserted.
- The third field can be among other things "Delete" of "Delete Target Word" (see below).
- Either the first or the third field can be "Insert". If the first field, then the third field has the inserted word number, or if user defined syncat, it has the target word(s) itself. If the third field, then the inserted word is in the first field, or otherwise feature values to be inserted are in the second field (see below).
- The second field can have subfields delimited by "^", for which the first subfield is the usual and the next subfield is empty, otherwise a series of one or more subfields like the following: an integer, followed by "|", followed by a comma-separated list of feature names, in which case the third field is either "Insert" or "-1". The integer in question denotes the line in the corresponding InputStructure from which those enumerated features are copied from for this inserted word. (? unsure whether more than one table entry allowed here or not).
- The first field can be (an optional modifier preceding) "Move" followed by positive integer followed by "!", all this prepended before what would normally be in the first field (after optional modifier).
- The first field can be "Copy" or "CopyPhrase" followed by a nonnegative integer.

field 3 can be empty, or -1, or a TL word, or comma-separated integers
or Delete

Rules_Spellout does not adhere to any of this.

CopyPhrase: //the beginning of the copy sequence is a phrase or clause, so don't add the word in the current column


    """

    #--------------------------------------------------------------------------

    # The following is information on how the Insert, Delete, Move and
    # Copy operations are defined and how they are encoded in an
    # OutputStructure (cf. CExecuteRules::ApplyOutputStructure; see also
    # CTA1Doc::SetRestructuringRule).

    # The ApplyOutputStructure scans an OutputStructure (each scan runs
    # from begin to end) 3 times, to process 1) Insert and Copy, 2) Move
    # and 3) Delete.  For Insert and Copy, this keyword appears at the
    # (inserted) line of the OutputStructure where the new item is to
    # appear. For Copy, the number following this keyword denotes the
    # "source" line (0-based) of the OutputStructure "before" the
    # insertions are made. Equivalently, it is the (line) index into the
    # corresponding InputStructure.

    # A word can be Inserted. A word, phrase (maybe even a clause?) can be
    # copied. If a phrase is copied, then the line for the phrase is marked
    # with the keyword Copy, and the "word" lines of the phrase are marked
    # with the keyword CopyPhrase. The destination for a copy can't be a
    # word but it can be a specified location with in a phrase.

    # For the Move pass, the number after this keyword is the (0-based)
    # line number of the "target" location of the move, using the
    # numbering "after" pass 1 is complete. The destination of the move
    # must be the beginning of a phrase or clause (this is at least true
    # for Rules_Movement). An Inserted word can't be Moved (or Copied).

    # For Delete, the Delete keyword for a phrase (clause) is present on
    # every line of the phrase (clause) and its contents, including the
    # closing punctuation.  Using "Delete Target Word" deletes the word
    # but will "leave source and features."

    # The GUI allows (and creates OutputStructure for) certain things that
    # seem not to make sense, like moving a clause into one of its
    # phrases, or copying phrase A into phrase B and vice bersa in the
    # same OutputStructure. Unknown how these would behave during a
    # generate.

    #--------------------------------------------------------------------------

    # Check for the case of multple structures delimited by special chars.
    # check that the user has already split these up.
    assert in_.find(_utils.delim_rule_type(rule_type)) == -1, (
        'Error: must split multiple structures and pass in individually.')

    out = []

    if in_ == '':
        return out

    # Split on crlf to separate "constituents"
    # Note here, this is not exactly the same as a grammatical consstituent
    # because it could be for example a closing parenthesis etc.
    # Orig code: this is done with a while loop

    for line in in_.split('\r\n'):

        if (rule_type == _utils.RULE_TYPES['Rules_Spellout'] or
            rule_type == _utils.RULE_TYPES['Rules_PronounSpellout']):
            out.append(str(line))
            continue

        if line == '':
            continue

        tokens = line.split('~|')
        assert len(tokens) in [0, 1, 2, 4]

        # fields description from orig code:
        # 1. source words
        # 2. features
        # 3. target word
        # 4. inserted flag

        num_delim = line.count('~|')

        w, f, r, i = (tokens + ['', '', ''])[0:4]

        # Process any modifier present.
        # & = optional
        # % = obligatory
        (modifier, w2) = ('',   ''   ) if w == '' else (
                         (w[0], w[1:]) if re.search(r'^[*&^]', w) else
                         (w[0], w[1:]) if re.search(r'^[%]', w) else
                         ('',   str(w)))
        modifier_active = modifier if re.search(r'^[%]', modifier) else ''

        # Get copied features if present.
        is_f_subfields = '^' in f
        (f2, c) = tuple(f.split('^', 1)) if is_f_subfields else (str(f),'')

        # Check does the second field denote a special situation.
        is_user_defined_syncat = bool(re.search(r'^&', f2)) or (
            bool(re.search('~!~', f2)))

        user_defined_syncat = (re.sub(r'~!~.*', '', re.sub(r'^&', '', f2))
             if is_user_defined_syncat else None)

        user_defined_syncat_word = (f2.split('~!~')[1] if '~!~' in f2 else
            str(r) if is_user_defined_syncat else None)

        #f3 = str(f2)
        #is_table_target_words = '^' in r
        #if is_user_defined_syncat:
        #    f3 = f2[1:] + '~!~' + r
        #    q = -4
        #elif is_table_target_words:
        #    q = str(r)
        #elif (rule_type == RULE_TYPES['Rules_ComplexConcepts'] and
        #      r != 'Insert' and r != ''):
        #    q = str(r)
        #else:
        #    q = None

        # Insert.

        is_insert_field1 = w2 == 'Insert' # inserted word info is in r
        is_r_wordref = r.isdigit()
        is_r_empty = r == ''
        is_insert_field3 = r == 'Insert' # inserted word info is in field 1,
                               # feature values copy source, if any, in field 2

        # Copy.

        is_copy = bool(re.search(r'^Copy[0-9]+', w2))
        is_copy_phrase = bool(re.search(r'^CopyPhrase[0-9]+', w2))

        is_insert_or_copy_flag = 0 if i=='0' else 1 if i=='1' else None

        copy_source = int(w2.replace('Copy', '')) if is_copy else None
        copy_phrase_source = (
            int(w2.replace('CopyPhrase', '')) if is_copy_phrase else None)

        assert r in ['', '-1'] or r.isdigit() or not (
            is_copy or is_copy_phrase)

        # Move.

        is_move = bool(re.search(r'^Move![0-9]+', w2))
        move_destination = (
            int(w2.replace('Move!', '')) if is_move else None)
        assert r in ['', '-1'] or not is_move

        # Delete.

        is_delete = r == 'Delete'
        is_delete_target_word = r == 'Delete Target Word'

        # Check that at most only one us set.
        assert sum([is_insert_field1, is_insert_field3, is_copy, is_copy_phrase,
                    is_move, is_delete, is_delete_target_word]) <= 1

        copied_feature_values_source = []
        copied_feature_values = []

        for s in c.split('^'):
            if '|' in s:
                cfvs, cfv = tuple(s.split('|'))
                copied_feature_values_source.append(cfvs)
                copied_feature_values.append(cfv)

        # Add info for this "constituent" to output.

        out.append({
            'num_delim': num_delim,
            #
            'modifier': modifier,
            'w2': w2,
            'f2': f2,
            'c': c,
            'r': r,
            'i': i,
            'is_f_subfields': is_f_subfields,
            'is_user_defined_syncat': is_user_defined_syncat,
        })

    return out

#------------------------------------------------------------------------------

def import_output_structures(in_: str, rule_type: int) -> list:
    """Do import_output_structure for a string with muliple structures."""

    # special chars delimit multiple rules. If occurs, it is preceded by crlf,
    # Also it will occur at the very end of the multiple structures string.
    # It does not have following crlf.
    
    # Split the multiple structures.
    in_structure_strings = in_.split(_utils.delim_rule_type(rule_type))

    out = []

    # Loop over subrules.

    for in_structure_string in in_structure_strings:
        out.append(import_output_structure(in_structure_string, rule_type))

    if (rule_type == _utils.RULE_TYPES['Rules_Spellout'] or
        rule_type == _utils.RULE_TYPES['Rules_PronounSpellout']):
        return out

    # Special code to ensure exact reconstruction match for existing tables.

    is_final_cr = len(in_) >= 2 and in_[-2:] == '\r\n'
    out.append(is_final_cr)

    return out

#------------------------------------------------------------------------------

def export_output_structure(in_: list, rule_type: int) -> str:
    """Inverse of the import_output_structure operation."""

    if (rule_type == _utils.RULE_TYPES['Rules_Spellout'] or
        rule_type == _utils.RULE_TYPES['Rules_PronounSpellout']):
        return '\r\n'.join(in_)

    out = ''

    # Loop over "constituents".

    for elt in in_:

        if elt == '':
            continue

        w = elt['modifier'] + elt['w2']
        out += w
        if elt['num_delim'] >= 1:
            out += '~|' # delimiter

        f = elt['f2'] + ('^' if elt['is_f_subfields'] else '') + elt['c']
        out += f
        if elt['num_delim'] >= 2:
            out += '~|' # delimiter

        out += elt['r']
        if elt['num_delim'] >= 3:
            out += '~|' # delimiter

        out += elt['i']
        if elt['num_delim'] >= 4:
            out += '~|' # delimiter

        out += '\r\n' # delimiter

    return out

#------------------------------------------------------------------------------

def export_output_structures(in_: list, rule_type: int) -> str:
    """Inverse of the import_output_structures operation."""

    out_list = []

    assert len(in_) >= 1

    if (rule_type == _utils.RULE_TYPES['Rules_Spellout'] or
        rule_type == _utils.RULE_TYPES['Rules_PronounSpellout']):
        return _utils.delim_rule_type(rule_type).join(
            [export_output_structure(elt, rule_type) for elt in in_])

    # Loop over subrules.

    for elt in in_[:-1]:

        out_list.append(export_output_structure(elt, rule_type))

    out = _utils.delim_rule_type(rule_type).join(out_list)

    # Special code to ensure exact reconstruction match for existing tables.

    is_final_cr = in_[-1]
    is_final_cr_this = len(out) >= 2 and out[-2:] == '\r\n'

    if is_final_cr and not is_final_cr_this:
        out += '\r\n'

    if is_final_cr_this and not is_final_cr and len(out) >= 2:
        out = out[:-2]

    return out

#==============================================================================
