#!/usr/bin/env python3
"""============================================================================

Handle Rules_Spellout table from <MyLanguage>.mdb file.

============================================================================"""

import re

import _utils
from _input_structures import *
from _output_structures import *
from _spellout_tables import *

#==============================================================================

class RulesSpellout:
    """
    Handle Rules_Spellout table from <MyLanguage>.mdb file.

    -----------------------------------------------------------------------
    Notes

    see CTA1Doc::GetRulesType
    see ExecuteRules.cpp, lines 13154f

    RuleType:
    0: Simple
    1: Morphophonemic
    2: Lexical Form Selection
    3: Table
    4: Phrase Builder
    5: Suppletive Forms
    NOTE: may be only a subset of these, depending on syncat (see code below).

    NOTE: these cases present different dialog window forms, making this
    complicated.

    It would appear phrases and clauses can only take Simple and Table
    types, and in fact somewhat restrictive: only Structures, Features,
    New Word, Word's Tag.

    Morpheme:
    0, 3; phrase or clause: the "New Word" to insert

    Parsing:
    0, 3; phrase or clause: "Word's Tag" - an indicator (POS, or
      user-defined here), inserted here, used later in phrase structure
      rules. It is a (sometimes user defined) WORD CATEGORY.
      The tags show up downstream in the phrase structure rules, in the
      "tree" view

    RulesParsing:
    0, 3: "^"-delimited feature values string for word, phrase,
    clause, in that order, of (presumably) trigger word for match

    Modification: Simple, Table
    0: Prefix
    1: Suffix
    2: Infix
    3: New translation
    4: Add Word
    5: Circumfix
   #6. Lexical Form Selection
       (NOTE: this last doesn't initially appear, but it does if you switch
        from Simple to Table and back again NOTE: this appears to not work)

    Modification: Morphophonemic
    0: prefix
    1: infix, treated as prefix
    2: infix, treated as suffix
    3: suffix
    4: circumfix, treated as prefix
    5: circumfix, treated as suffix
    6. Lexical Form Selection
        (this last item: maybe?)

    BaseForm: the rule's base form - options are specific to RuleType.
    it is the word form to take as the basis for the modification.
    cases:
    "Current entry"
    "Stem"
    "Citation Form"
    "New Translation"  (only for Phrase Builder case)
    "Delete Word"   (only for Phrase Builder case)
    ""

    TargetWord: this seems to be the same as the "Trigger Word" in many
      dialogs (disabled for Phrase Builder case).
    cf. ExecuteRules.cpp, lines 13288f
    is "excluded" if the first character of the string is "."
    the rest is a comma-delimited list of target word ids.

    NOTE: here and elsewhere, when there is a comma-separated features string,
    the slot between two specific consecutive commas (or begin or end)
    represents a feature, and multiple single-letter feature values
    can be represented therein.

see CTA1Doc::SetSpelloutRule
see CSpelloutRuleDlg::LoadSourceCombo
see CSpelloutRuleDlg::OnOK
see CExecuteRules::ApplyModification

-----
SIMPLE
-----

Example: Simple; Noun or any of the other 7 word types
  RulesParsing has the feature string
  Morpheme has the affix (or New Translation, or Add Word) text
    if reduplication e.g. CV first 2 chars of stem, "*02C,|V,||||" - * = redupl,
      02 = 2 chars; | delimits 5 slots; "C," can have multiple options per slot
    if Circumfix: Morpheme is first-part then + then last-part
    if prefix or suffix: the prefix or suffix
    redup only available for prefix and suffix
  Parsing has the "tag" - an identifier for the modification being done here,
    presumably can be used later in phrase structure rule.
    if New Translation, not used
    if Add Word, then has POS as options (see below).
    if others, has an option like "Pre-Nominal"
    you can also type in something "made up" for downstream use (specif,
      a "new constituent" used downstream in phrase structure rules), may (?) be
      correlated with word form in lexicon (??)
  InfixPlaceHolder is usually "", however for infix case: either a special
    string that was inserted manually into the base that the infix replaces,
    or a number chars distance from begin or end of base
  TargetWord = trigger word
  if New Translation, ignore BaseForm
  if Add Word, select Word's Tag (e.g. Adjectives), then select word from
    lexicon, and features. Parsing = Adjectives followed by "^" followed by
    features string (NOTE features box appears for this mode (if there "are" any features for this syncat) (?)).
    Morpheme is word number (source or target?). Word is
    added "after" the original word (put in propoer position later, I assume)
  nType = 1 standard spellout, = 2 pronoun spellout (CTA1Doc::SetSpelloutRule)

Example: Simple; Noun Phrases or any other phrase
  dialog only allows Structures, Features (head word, phrase, clause), New Word,
    Word's Tag (POS, Opening (alt Closing) Implicit Marker, or something new
    you can add here).

Example: Simple; Clause: same as prev, but only Clause features

Example: Simple, User Defined: seems same but only clause features.
#NOTE: where is user defined syncat defined?
it is not defined in the lexicon.
Example: "there" is classified as noun in lexicon, however it is
classified as "Existential Expletive" in just one place, the Movement Rules (!).
Apparently this information is propagated back into the spellout rules list (!).

Example: Simple, All Categories: this case not allowed

-----
TABLE
-----

Example: Table. It seems this is just like the Simple rules, except what was
the Features selection now becomes the column head, and the morpheme becomes
the table entry.
/// Table table entry is morpheme ///
note for circumfix case, the pre and suf are put together, joined by "-"
apparently everything in top of box (rule type, trigger word, etc.) is global
across all layers and rules per layer (CHECK)
looks like the Morpheme string is empty
RulesParsing stores the table: example (please disregard newlines here) (myfeaturestring = mywordfeaturevals^myphrasefeaturevals^myclausefeaturevals^):

mylayername1|mygeneralfeatures>|<mynumrows|mynumcols|
myrowname1@myfeaturestring1|
myrowname2@myfeaturestring2|
mywidthnum1|
mywidthnum2|mycolname1@myfeaturestring3|
mywidthnum3|mycolname2@myfeaturestring4|
myeltrow1col1|myeltrow1col2|myeltrow2col1|myeltrow2col2|
~!~
myeltcommentsrow1col1^myeltcommentsrow1col2^myeltcommentsrow2col1^myeltcommentsrow2col2^
~!!~

#NOTE the above is repeated per-layer
#NOTE: Parsing holds the tag, and if appropriate, "^" then the feature sring for the relevant syncat. Note this is global across layers and subrules. Same, I think, for "Simple" above.
#NOTE: table elt can be empty
#NOTE: rowname and features can both be ommitted. colname cannot be empty
#NOTE: the GUI seems confused if the rowname in one layer is the prefix of a
  rowname in another
#NOTE: we also have option for Lexical Form Selection ("form" in lexicon)
#NOTE: reduplication case: Morpheme is same as Simple rule (2-digint num
  is "01", not used), RulesParsing entry just has "*" and 2-digit number.

-----
LEXICAL FORM SELECTION
-----

Example: Lexical Form Selection
the only option here is to select the BaseForm ("Select Form:")
has the usual Structures, trigger word, excluded, features - all these for doing
  match
no "Type of Modification:"
#NOTE: BaseForm doesn't need to be one of those on the list.

-----
SUPPLETIVE FORMS
-----

see CSpelloutRuleDlg::SaveSuppletiveFormsLayer

Example: Suppletive Forms:
no Type of Modification (= 0)
no Structures
no Select Form
has Features, trigger word
has layers but just 1 row
column head is features string, entry is morpheme
seems to be like Table above - Morpheme is empty, RulesParsing contains a table spec.
here you actually enter the form itself, not the name of the form from
  the lexicon.
#NOTE: for lexicon case, ths rule can be built more easily by just typing the
  suppletive form into the relevant field to override the general rule
it would seem (?) you put this in the spellout rules instead of lexical form rules if it is very dependent on context (?)

-----
PHRASE BUILDER
-----

see CSpelloutRuleDlg::SavePhraseBuilderLayer
see CExecuteRules::ExecuteRule
see CExecuteRules::CheckSpelloutRulePhraseBuilderStructure

Example: Phrase Builder
no Type of Modification button
  (Modification = 0 for Lexical Form, =1 for Feature Value (see below))
no Structures button
no Select Form button
no trigger word
no "... Tag" button
the "Rule's Output" (= table entry type, I presume) is global across layers,
  = Select a Lexical Form or Set a Feature Value
for Feature Value case, can select feature name (global across layers)
lexical form is more common
Interestingly, each row is associated with a "structure"
the set of columns can be different for different layers (likewise for Table)
column 1 allows you to select the BaseForm of the syncat in the relevant column
  or feature value relevant to the row
#NOTE the column with the name of the syncat typically isn't filled in, it is
  just a placeholder to show the context of the other columns (only change if
  you want to do a New Translation)
perhaps the column name functions in the role of "tag" for downstream use,
  specif. PSR - YES!
BaseForm is "Current Entry", seems ignored
Morpheme is "0", seems ignored
NOW, RulesParsing stores the table. it is very similar as with the Table case
  (for now, disregard newlines below) (this is Select the Lexical Form case):

mylayername1|mygeneralstructures>|<mynumrows|mynumcols|
myrowname1@
myinputstructure1
-*-
myinputstructure2
-*-
^~^
myoutputstructure1
-*-
myoutputstructure2
-*-
>|<
mywidthnum1|
mywidthnum2|mycolname1@|
mywidthnum3|mycolname2@|
mywidthnum4|mycolname3@|
myeltrow1col1|myeltrow1col2|myeltrow1col3|
myeltrow2col1|myeltrow2col2|myeltrow2col3|
~!!~

mygeneralstructures is optional and if present looks like the following. it contains structures that must be matched for "any" of the this layer's rules to be applied. note it has the same pattern as the per-row structures string.

mygeneralinputstructures^~^mygeneraloutputstructures

///phrase builder table entry is morpheme (lexical form or feature value ///
#NOTE the above is repeated per-layer
#NOTE: table elt can be empty
#NOTE: for Feature Value case:
Column header is (wrongly) Select a Lexical Form, should be Set a Feature Value
  but not important, apparently.

-----

input structure and output structure is very similar to elsewhere, with these
differences:

- "!" preceding input structure means invert the match (this is per-structure)
- each line of input structure has 3 fields (some possibly empty), 2 delimiters
  (exactly), and ending CR
- output structure has exactly same number of lines as input structure, of
  the form "|" followed by CR, possibly preceded by "Delete". That is all (!)
  (no Delete in input structure)
- input structure modifiers & and ^ work
- word reference has the form 0---- in first field and word number (or comma
  separated word numbers) in 3rd field
- input structure 3rd field bay be blank or -1
- ...

-----
MORPHOPHONEMIC
-----

cf. CSpelloutRuleDlg::SetupMorphophonemicRule
Example: Morphophonemic:

BaseForm = "Current entry" (presumably ignored)
InputStructures = ""
OutputStructures = ""
Morpheme = "|"-delimited "tags" to indicate which prefix [class]
Infix (= InfixPlaceHolder) = feature string, per dialog
  //for morpho rules, word's features saved in InfixPlaceHolder

RulesParsing:
first char = "*" if stem reduplication else ""
then "1-" if epipenthesis else
     "2-" if morpheme reduplication else ""
then "1" for "beginning of prefix changes" else
     "2' for "prefix completely changes" else
     "0" for no morpheme change
then "1" for stem change else "0"
then "0" (specifying stem with phonetic features),else:
     "1" (stem by alphabetic)
then "0" (specifying morpheme with phonetic features), else:
     "1" (morpheme by alphabetic)

then if morphemespec==0: 5 "|"-delim phonemes string, each ","-delim ","-ended
                         1-chars, for old morpheme, else:
     old morpheme text up to "^"

then "^"

then if morpheme redup: integer redup code, else
     if epithenthesis: characters to insert else
     if morphemespec==0: phonemes string for new morpheme, else:
     new morpheme text up to "^"

then "^"

then if stemspec==0: phonemes string for old stem, else:
     old stem text up to "^"

then "^"

then if stemspec==0: phonemes string for new stem, else:
     new stem text up to "^"

#NOTE: from video, believe circumfix 2 parts delimited by "+"

Parsing: contains new morpheme text

-----

#NOTE: layers (likewise rows) are searched last to first

#NOTE: it seems you can add a (tagged) prefix to denote some characteristic of the word, you will pick up downstream, and remove the prefix - so it is only to communicate information to downstream rule, but does not appear in final text.

    -----------------------------------------------------------------------
    """

    RULE_TYPE = _utils.RULE_TYPES['Rules_Spellout']

    # List of fields that are needed for the translation/generation.

    FIELDNAMES_IMPT = [
        'Status',
        'SyntacticCategory',
        'RuleType',
        'InputStructures',
        'OutputStructures',
        'RulesParsing',
        'Modification',
        'BaseForm',
        'Morpheme',
        'Parsing',
        'InfixPlaceHolder',  #//for morpho rules, word's features saved in InfixPlaceHolder
        'TargetWord',
    ]

    # Define all fields associated wtih this table.

    FIELDNAMES = [
        'ID', # it would seem this not needed for translation
        'GroupName', # ??? is this needed for the translation
        'RulesName', # this is human-readable, seems not needed for translation
        'Comment',
        'CommentFonts',
        'NameFonts',
        'GrammarTopics',
        'TableComments',
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

        INFIX_PARSING_KEY = 'InfixParsing' if 'InfixParsing' in (
            self.FIELDNAMES) else 'InfixPlaceHolder'
        TARGET_WORD_KEY = 'TargetWord' if 'TargetWord' in (
            self.FIELDNAMES) else 'TriggerWords'

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
            syncat = str(field)

            # Get the rule type.
            field = rule['RuleType'] = table[i+1][sfoo.index('RuleType')]
            assert field in _utils.SPELLOUT_RULE_TYPES.values()
            rule_type = str(field)

            # Validate combinations of settings.
            # cf. CSpelloutRuleDlg::LoadRuleTypeCombo
            assert (
                    rule_type == _utils.SPELLOUT_RULE_TYPES['Morphophonemic'] or
                   (rule_type == _utils.SPELLOUT_RULE_TYPES['Phrase Builder']
                    and self.RULE_TYPE != _utils.RULE_TYPES['Rules_Lexical'])
                   ) or not (
                    syncat == _utils.SYNCATS['all']
                   )
            assert (
                    rule_type == _utils.SPELLOUT_RULE_TYPES['Simple'] or
                    rule_type == _utils.SPELLOUT_RULE_TYPES['Morphophonemic'] or
                    rule_type == _utils.SPELLOUT_RULE_TYPES['Table']
                   ) or not (
                    syncat == _utils.SYNCATS['user-defined']
                   )
            assert (
                    rule_type == _utils.SPELLOUT_RULE_TYPES['Simple'] or
                    rule_type == _utils.SPELLOUT_RULE_TYPES['Table']
                   ) or not (
                    _utils.is_syncat_clause(syncat) or
                    _utils.is_syncat_phrase(syncat) or
                   (
                    _utils.is_syncat_bottomword(syncat) and not
                    self.RULE_TYPE == _utils.RULE_TYPES['Rules_Lexical']
                   )
                   )
            assert (
                    rule_type == _utils.SPELLOUT_RULE_TYPES['Simple'] or
                    rule_type == _utils.SPELLOUT_RULE_TYPES['Morphophonemic'] or
                    rule_type == _utils.SPELLOUT_RULE_TYPES[
                                                    'Lexical Form Selection'] or
                    rule_type == _utils.SPELLOUT_RULE_TYPES['Table'] or
                   (rule_type == _utils.SPELLOUT_RULE_TYPES['Phrase Builder']
                    and self.RULE_TYPE != _utils.RULE_TYPES['Rules_Lexical']) or
                    rule_type == _utils.SPELLOUT_RULE_TYPES['Suppletive Forms']
                   ) or not (
                    _utils.is_syncat_topword(syncat)
                   )

            # Parse the input structures.
            if 'InputStructures' in self.FIELDNAMES:
                field = rule['InputStructures'] = table[i+1][sfoo.index(
                             'InputStructures')]
                # Is the match action predicate to be inverted.
                is_exclude_inputstructures = len(field) > 0 and field[0] == '!'
                # Finish parsing. note this still has the exclude marker.
                rule['InputStructures'] = import_input_structures(field,
                    rule_type=self.RULE_TYPE)

            # Parse the output structures.
            if 'OutputStructures' in self.FIELDNAMES:
                field = rule['OutputStructures'] = import_output_structures(
                    table[i+1][sfoo.index('OutputStructures')],
                    rule_type=self.RULE_TYPE)

            # Get type of modification done by the rule.
            field = rule['Modification'] = table[i+1][sfoo.index(
                         'Modification')]
            assert field.isdigit() and int(field) >= 0 and int(field) <= 6
            modification = str(field)

            # Target or "trigger" word to be matched for rule to fire.
            field = rule[TARGET_WORD_KEY] = table[i+1][sfoo.index(
                         TARGET_WORD_KEY)]
            # Is the match action predicate to be inverted.
            is_exclude_targetwords = len(field) > 0 and field[0] == '.'
            # Comma-separated (and possibly terminated) list of numbers.
            wordnums = (field[1:] if is_exclude_targetwords else
                field).split(',')
            assert all(w=='' or w.isdigit() for w in wordnums)
            rule[TARGET_WORD_KEY] = [wordnums, is_exclude_targetwords]

            # Get the tag, for use in later rules.
            if 'Parsing' in self.FIELDNAMES:
                field = rule['Parsing'] = table[i+1][sfoo.index('Parsing')]

            # Get descriptor of base form of the word to modify.
            field = rule['BaseForm'] = table[i+1][sfoo.index('BaseForm')]
            # This is not always true, depending on rule type.
            #assert field in _utils.SPELLOUT_BASEFORM_NAMES

            # Form name, as defined by user.
            if 'FormName' in self.FIELDNAMES:
                field = rule['FormName'] = table[i+1][sfoo.index('FormName')]

            # 
            if 'ExtraMorpheme' in self.FIELDNAMES:
                field = rule['ExtraMorpheme'] = table[i+1][sfoo.index(
                             'ExtraMorpheme')]

            #-----
            # Handle "Simple" rules.
            #-----
            if rule_type == _utils.SPELLOUT_RULE_TYPES['Simple']:

                # Specify features for match. Delimiter is "^"; 3 fields:
                # word features, phrase features, clause features.
                field = rule['RulesParsing'] = (
                    table[i+1][sfoo.index('RulesParsing')].split('^'))
                assert len(field) == 3 or (
                    len(field) == 1 and field[0] == '') or (
                    len(field) == 1 and field[0] == ',') or (
                    len(field) == 1 and self.RULE_TYPE ==
                        _utils.RULE_TYPES['Rules_Lexical'])
                # Not sure why the following doesn't work
                #assert len(field) == 3 or (
                #    syncat == _utils.SYNCATS['user-defined'] or
                #    syncat == _utils.SYNCATS['clause'])
                #assert len(field) == 1 or not (
                #    syncat == _utils.SYNCATS['user-defined'] or
                #    syncat == _utils.SYNCATS['clause'])

                # Morpheme.
                field = rule['Morpheme'] = table[i+1][sfoo.index('Morpheme')]
                # TODO: strip off trailing (comments?).
                MODIFICATIONS = _utils.SPELLOUT_MODIFICATION_SIMPLE_TABLE_TYPES
                # Note circumfix case has two parts separated by "+".
                assert '+' in field or not (
                       modification == MODIFICATIONS['Circumfix'])
                # Check for reduplication marker.
                is_redup = len(field) > 0 and field[0] == '*'
                assert (modification == MODIFICATIONS['Prefix'] or
                        modification == MODIFICATIONS['Suffix'] or
                        not is_redup)
                redup_type = None
                phoneme_strings = None
                if is_redup:
                    field2 = field[1:]
                    redup_type = field2[1:2] if field2[0] == '0' else (
                        field2[:2] )
                    assert redup_type.isdigit()
                    # Note last element is comments.
                    phoneme_strings = field2[2:].split('|')
                    assert len(phoneme_strings) == 5 + 1

                # Get where to put infix.
                field = rule[INFIX_PARSING_KEY] = table[i+1][sfoo.index(
                             INFIX_PARSING_KEY)]
                is_int = bool(re.fullmatch(r'-?\d+', field))
                is_infix_from_begin = is_int and int(field) > 0
                is_infix_from_end = is_int and int(field) < 0
                infix_distance = abs(int(field)) if is_int else 0

            #-----
            # Handle "Morphophonemic" rules.
            #-----
            if rule_type == _utils.SPELLOUT_RULE_TYPES['Morphophonemic']:

                field = rule['RulesParsing'] = table[i+1][sfoo.index(
                             'RulesParsing')]

                fields = field.split('^')
                assert len(fields) == 4

                is_stem_redup = fields[0][:1] == '*'
                if is_stem_redup:
                    fields[0] = fields[0][1:]

                is_epipenthesis = fields[0][:2] == '1-'
                is_morpheme_redup = fields[0][:2] == '2-'
                if is_epipenthesis or is_morpheme_redup:
                    fields[0] = fields[0][2:]

                morpheme_change = fields[0][0]
                is_stem_change = fields[0][1] == '1'
                is_stem_spec_alphabetic = fields[0][2] == '1'
                is_morpheme_spec_alphabetic = fields[0][3] == '1'
                fields[0] = fields[0][4:]

                orig_morpheme, orig_morpheme_phoneme_strings = None, None

                if is_morpheme_spec_alphabetic:
                    orig_morpheme = fields[0]
                elif not is_morpheme_spec_alphabetic:
                    orig_morpheme_phoneme_strings = fields[0].split('|')

                morpheme_redup_code, epipenthesis_chars =  None, None
                new_morphemes_phonemes_strings, new_morpheme = None, None

                if is_morpheme_redup:
                    morpheme_redup_code = fields[1]
                elif epipenthesis_chars:
                    epipenthesis_chars = fields[1]
                elif not is_morpheme_spec_alphabetic:
                    new_morphemes_phonemes_strings = fields[1]
                else:
                    new_morpheme = fields[1]

                orig_stem, orig_stem_phoneme_strings = None, None

                if is_stem_spec_alphabetic:
                    # Can be a string of letters, or comma-separated letters.
                    orig_stem = fields[2]
                elif not is_stem_spec_alphabetic:
                    orig_stem_phoneme_strings = fields[2].split('|')

                new_stem, new_stem_phoneme_strings = None, None

                if is_stem_spec_alphabetic:
                    # Can be a string of letters, or comma-separated letters.
                    new_stem = fields[3]
                elif not is_stem_spec_alphabetic:
                    new_stem_phoneme_strings = fields[3].split('|')

                # This holds the affix tags for this case.
                field = rule['Morpheme'] = table[i+1][sfoo.index(
                             'Morpheme')].split('|')

                # Get where to put infix.
                field = rule[INFIX_PARSING_KEY] = table[i+1][sfoo.index(
                             INFIX_PARSING_KEY)].split('^')

            #-----
            # Handle "Lexical Form Selection" rules.
            #-----
            if rule_type == (
                _utils.SPELLOUT_RULE_TYPES['Lexical Form Selection']):

                # Specify features for match. Delimiter is "^"; 3 fields:
                # word features, phrase features, clause features.
                field = rule['RulesParsing'] = (
                    table[i+1][sfoo.index('RulesParsing')].split('^'))
                assert len(field) == 3 or (
                    len(field) == 1 and field[0] == '') or (
                    len(field) == 1 and field[0] == ',') or (
                    len(field) == 1 and self.RULE_TYPE ==
                        _utils.RULE_TYPES['Rules_Lexical'])
                # Not sure why the following doesn't work
                #assert len(field) == 3 or (
                #    syncat == _utils.SYNCATS['user-defined'] or
                #    syncat == _utils.SYNCATS['clause'])
                #assert len(field) == 1 or not (
                #    syncat == _utils.SYNCATS['user-defined'] or
                #    syncat == _utils.SYNCATS['clause'])

                field = rule['Morpheme'] = table[i+1][sfoo.index(
                             'Morpheme')]
                assert field == ''

                # Get where to put infix.
                field = rule[INFIX_PARSING_KEY] = table[i+1][sfoo.index(
                             INFIX_PARSING_KEY)]

            #-----
            # Handle "Table" rules.
            #-----
            if rule_type == _utils.SPELLOUT_RULE_TYPES['Table']:

                field = rule['RulesParsing'] = import_spellout_tables(
                    table[i+1][sfoo.index('RulesParsing')],
                    rule_type=self.RULE_TYPE, rule_subtype=rule_type)

                field = rule['Morpheme'] = table[i+1][sfoo.index(
                             'Morpheme')]
                is_redup = len(field) > 0 and field[0] == '*'
                if is_redup:
                    assert (modification == MODIFICATIONS['Prefix'] or
                            modification == MODIFICATIONS['Suffix'])
                    field2 = field[1:]
                    redup_type = field2[1:2] if field2[0] == '0' else (
                        field2[:2] )
                    assert redup_type.isdigit()
                    # Note last element is comments.
                    phoneme_strings = field2[2:].split('|')
                    assert len(phoneme_strings) == 5 + 1
                else:
                    assert field == ''

                # Get where to put infix.
                field = rule[INFIX_PARSING_KEY] = table[i+1][sfoo.index(
                             INFIX_PARSING_KEY)]
                is_int = bool(re.fullmatch(r'-?\d+', field))
                is_infix_from_begin = is_int and int(field) > 0
                is_infix_from_end = is_int and int(field) < 0
                infix_distance = abs(int(field)) if is_int else 0

            #-----
            # Handle "Phrase Builder" rules.
            #-----
            if rule_type == _utils.SPELLOUT_RULE_TYPES['Phrase Builder']:

                field = rule['RulesParsing'] = import_spellout_tables(
                    table[i+1][sfoo.index('RulesParsing')],
                    rule_type=self.RULE_TYPE, rule_subtype=rule_type)
                    
                field = rule['Morpheme'] = table[i+1][sfoo.index(
                             'Morpheme')]

                # Get where to put infix.
                field = rule[INFIX_PARSING_KEY] = table[i+1][sfoo.index(
                             INFIX_PARSING_KEY)]
                assert field == ''

            #-----
            # Handle "Suppletive Forms" rules.
            #-----
            if rule_type == _utils.SPELLOUT_RULE_TYPES['Suppletive Forms']:

                field = rule['RulesParsing'] = import_spellout_tables(
                    table[i+1][sfoo.index('RulesParsing')],
                    rule_type=self.RULE_TYPE, rule_subtype=rule_type)

                field = rule['Morpheme'] = table[i+1][sfoo.index(
                             'Morpheme')]
                assert field == ''

                # Get where to put infix.
                field = rule[INFIX_PARSING_KEY] = table[i+1][sfoo.index(
                             INFIX_PARSING_KEY)]
                assert field == ''

            #-----

            self._rules.append(rule)

        self._is_set = True

#------------------------------------------------------------------------------

    def export_table(self) -> str:
        """Convert the parsed table back into string form."""

        assert self._is_set, (
           'Error: cannot export because table has not been set.')

        INFIX_PARSING_KEY = 'InfixParsing' if 'InfixParsing' in (
            self.FIELDNAMES) else 'InfixPlaceHolder'
        TARGET_WORD_KEY = 'TargetWord' if 'TargetWord' in (
            self.FIELDNAMES) else 'TriggerWords'

        result = []

        # Loop over table lines.
        for i in range(1+self._num_rules):
            result.append([])
            rule_type = '' if i == 0 else self._rules[i-1]['RuleType']
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

                if i != 0 and fieldname == TARGET_WORD_KEY:
                    field = (r'.' if field[1] else '') + r','.join(field[0])

                #-----
                # Handle "Simple" rules.
                #-----
                if rule_type == _utils.SPELLOUT_RULE_TYPES['Simple']:

                    if i != 0 and fieldname == 'RulesParsing':
                        field = '^'.join(field)

                #-----
                # Handle "Morphophonemic" rules.
                #-----
                if rule_type == _utils.SPELLOUT_RULE_TYPES['Morphophonemic']:

                    if i != 0 and fieldname == 'Morpheme':
                        field = '|'.join(field)

                    if i != 0 and fieldname == INFIX_PARSING_KEY:
                        field = '^'.join(field)

                #-----
                # Handle "Lexical Form Selection" rules.
                #-----
                if rule_type == _utils.SPELLOUT_RULE_TYPES[
                                                     'Lexical Form Selection']:

                    if i != 0 and fieldname == 'RulesParsing':
                        field = '^'.join(field)

                #-----
                # Handle "Table" rules.
                #-----
                if rule_type == _utils.SPELLOUT_RULE_TYPES['Table']:

                    if i != 0 and fieldname == 'RulesParsing':
                        field = export_spellout_tables(field,
                             rule_type=self.RULE_TYPE,
                             rule_subtype=rule_type)

                #-----
                # Handle "Phrase Builder" rules.
                #-----
                if rule_type == _utils.SPELLOUT_RULE_TYPES['Phrase Builder']:

                    if i != 0 and fieldname == 'RulesParsing':
                        field = export_spellout_tables(field,
                            rule_type=self.RULE_TYPE,
                            rule_subtype=rule_type)

                #-----
                # Handle "Suppletive Forms" rules.
                #-----
                if rule_type == _utils.SPELLOUT_RULE_TYPES['Suppletive Forms']:
                    pass

                    if i != 0 and fieldname == 'RulesParsing':
                        field = export_spellout_tables(field,
                            rule_type=self.RULE_TYPE,
                            rule_subtype=rule_type)

                #-----
                # Add field value to output.
                #-----
                result[-1].append(field)

        return result

#==============================================================================
