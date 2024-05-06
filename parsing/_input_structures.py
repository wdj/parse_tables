#!/usr/bin/env python3
"""============================================================================

Tools for InputStructure and InputStructures tables.

An InputStructure is a sequence of strings delimited by carriage return/
line feed delimieters '\r\n'.  Each string represents roughly a grammatical
constituent (clause, phrase, word), though closing punctuation for a
constituent, e.g., parenthesis, also has its own line. Each line consists
of 2 or 3 tokens delimited by "~|"

An InputStructures string is a series of InputStructure strings delimited by
'-*-' or sometimes '>|<'.

The syntax of these strings can vary slightly based on the rule type
(== which database table being considered).

============================================================================"""

import sys
import re

import _utils

#------------------------------------------------------------------------------

def import_input_structure(in_: str, rule_type: int) -> list:
    """This code reproduces the behavior of CExecuteRules::LoadInputStructure.
    """

    is_psr = rule_type == _utils.RULE_TYPES['Rules_PhraseStructure']

    # Check for the case of multple structures delimited by special chars.
    # check that the user has already split these up.
    assert in_.find(_utils.delim_rule_type(rule_type)) == -1, (
        'Error: must split multiple structures and pass in individually.')

    out = []

    if in_ == '':
        return out

    # Handle special case of Rules_FeatureCopying.
    in_string = in_
    source_loc = None
    dest_loc = None
    if rule_type == _utils.RULE_TYPES['Rules_FeatureCopying'] and (
        re.search(r'^[0-9]+\*\*[0-9]+\*\*', in_string)):
        source_loc, dest_loc, in_string = in_string.split('**')

    # The input string may have a comment if spellout cases.

    comment = ''

    # Split on crlf to separate "constituents"
    # Note here, this is not exactly the same as a grammatical consstituent
    # because it could be for example a closing parenthesis etc.
    # Orig code: this is done with a while loop

    for line in in_string.split('\r\n'):

        if line == '':
            continue

        if comment != '':
            comment += '\r\n' + line
            continue

        if re.search('^@!@', line):
            comment = str(line)
            #comment = str(line) if comment == '' else comment + '\r\n' + line
            continue

        # Orig code has this, which is also done here in
        # modified form:
        # parse T into T crlf S;
        # parse S into W ~| S
        # parse S into F ~| R

        tokens = line.split('~|')
        assert len(tokens) in [2, 3], (
           'Mismatch detected between the file format and this code.')
        # Now separate into: source word, features, target word.
        # (that's the simple case; can actually be more complex than this.)
        w, f, r = (tokens + [''])[0:3]

        # Separate source word into modifier and source word proper.
        # Orig code: parse W into [*&^] W if appropriate, and set modifier
        modifier = ''
        if re.search(r'^[*&^]', w):
            (modifier, w) = (w[0], w[1:])

        # The first token (without modifier) is one of the following:
        # - opening punctuation [ { ( if field 2 denotes clause or phrase
        # - closing punctuation ] } ) (and then nothing after first delimiter)
        # - "." which means it can match anything
        # - empty, which measn (?) can match anything
        # - comma-separated wordsense/word pairs (e.g., "Aafter")
        # - such pairs in parentheses (glosses), equivalent to "."
        # - a grammatical indicator like "A-Generic Genitive"
        # - the string "0----" which means field 3 has one of these:
        #   - comma-separated word numbers of TL words
        #   - empty - means nothing there to try to match (?)
        #   - "-1" - same as empty (?)
        #   - "-4" means field 2 has "special form" (see below), specifies
        #     a user defined syntactic category.
        #   note for case of "0----", the code says, "user entered a target
        #   word into a restructuring rule's input structure"

        # The second token (if not the special situation) has the
        # syntactic category identifier character, followed by "-",
        # followed (optionally) by the string of feature value characters.
        # If this last part omitted, presumably means it matches "any".

        # Note that, depending on the rule, it is possible (?) that
        # the input structure doesn't contain all the constituents
        # of the target clause to be matched, only the ones that
        # need to be checked for a match.

        # Orig code: case in which "word is only an example" (i.e., gloss)
        # NOTE: if w == '(' then it is a delimiter, not this situation.
        w2 = '.' if len(w) > 1 and w[0] == '(' else str(w)

        # Check does the second field denote a special situation.
        # Orig code: split on ~!~
        is_user_defined_syncat = re.search('~!~', f)

        # If it is this special situation, then split second token
        # into two subtokens, delimiter "~!~".
        input_features = str(f)
        f_left = str(f)
        f_right = ''
        r2 = str(r)
        if is_user_defined_syncat:
            # Orig code: reparse F into F ~!~ R
            f_left, f_right = f.split('~!~')[0:2]
            # Here f_left (input_features) is the name of the user defined
            # syntactic category specified here.
            input_features = str(f_left)
            # Ensure that it is properly marked with a leading "&".
            if input_features[0] != '&':
                input_features = '&' + input_features
            # f_right (if it is not empty) is (?) the actual TL word
            # with this syncat
            r2 = f_right

        # modifier is one of the following:
        # 1 = * = not present
        # 2 = & = optional
        # 3 = ^ = "if tagged as optional but concepts disallowed, in phrase
        #       structure rules this means obligatory but concepts disallowed"
        # Note the modifier character marks both the opening and closing
        # of a clause or phrase.

        input_present = 1 if modifier=='*' else 2 if modifier=='&' else 3
        if is_psr and modifier == '^' and r2 == '':
            input_present = 1

        # Strip off trailing comment if present. delimited by @!@,
        # possibly followed by comment fonts (comma separated integers).
        # This is used in spellout and pronoun spellout rules.
        r = r.split('!@!')[0]

        # Add info for this "constituent" to output.

        out.append({
            # needed in source code.
            'InputPresent': input_present,
            'InputFeatures': input_features,
            'InputTargetWords': r2,
            'InputSourceWords': w2,
            # used for later reconstruction of the string:
            'is_user_defined_syncat': is_user_defined_syncat,
            'modifier': modifier,
            'w': w,
            'f_left': f_left,
            'f_right': f_right,
            'r': r,
        })

    return [source_loc, dest_loc, out] if dest_loc != None else (
           [comment, out] if comment != '' else out)

#------------------------------------------------------------------------------

def import_input_structures(in_: str, rule_type: int) -> list:
    """Do import_input_structure for a string with muliple structures."""

    # special chars delimit multiple rules. If occurs, it is preceded by crlf,
    # Also it will occur at the very end of the multiple structures string.
    # It does not have following crlf.

    # Split the multiple structures.
    in_structure_strings = in_.split(_utils.delim_rule_type(rule_type))

    out = []

    # Loop over subrules.

    for in_structure_string in in_structure_strings:
        out.append(import_input_structure(in_structure_string, rule_type))

    # Special code to ensure exact reconstruction match for existing tables.

    is_final_cr = len(in_) >= 2 and in_[-2:] == '\r\n'
    out.append(is_final_cr)
    #if is_final_cr: print(in_)

    return out

#------------------------------------------------------------------------------

def export_input_structure(in_: list, rule_type: int) -> str:
    """Inverse of the import_input_structure operation."""

    # Handle special case of Rules_FeatureCopying.

    is_copying = len(in_) == 3 and isinstance(in_[0], str)
    is_comment = len(in_) == 2 and isinstance(in_[0], str)

    out = ''
    comment = ''
    in_dict = in_

    if is_copying:
        out = in_[0] + '**' + in_[1] + '**'
        in_dict = in_[2]
    elif is_comment:
        comment = in_[0]
        in_dict = in_[1]

    # Loop over "constituents".

    for elt in in_dict:

        if elt == '':
            continue

        out += elt['modifier']
        out += elt['w']
        out += '~|' # delimiter

        out += elt['f_left']
        if elt['is_user_defined_syncat']:
            out += '~!~' # delimiter
        out += elt['f_right']

        all_delims = (
            rule_type == _utils.RULE_TYPES['Rules_FeatureCopying'] or
            rule_type == _utils.RULE_TYPES['Rules_Spellout'] or
            rule_type == _utils.RULE_TYPES['Rules_PronounSpellout'] or
            rule_type == _utils.RULE_TYPES['Rules_PhraseStructure'])

        if all_delims:
            out += '~|' # delimiter
            out += elt['r']
        elif (rule_type == _utils.RULE_TYPES['Rules_Clitic'] or
              elt['r'] != '' or elt['w'] == '0----'):
            out += '~|' # delimiter
            out += elt['r']

        out += '\r\n' # delimiter

    if comment != '':
        out += comment

    return out

#------------------------------------------------------------------------------

def export_input_structures(in_: list, rule_type: int) -> str:
    """Inverse of the import_input_structures operation."""

    out_list = []

    assert len(in_) >= 1 

    # Loop over subrules.

    for elt in in_[:-1]:

        out_list.append(export_input_structure(elt, rule_type))

    out = _utils.delim_rule_type(rule_type).join(out_list)

    # Special code to ensure exact reconstruction match for existing tables.

    is_final_cr = in_[-1]
    is_final_cr_this = ('  ' + out)[-2:] == '\r\n'

    if is_final_cr and not is_final_cr_this:
        out += '\r\n'

    if is_final_cr_this and not is_final_cr and len(out) >= 2:
        out = out[:-2]

    return out

#==============================================================================
