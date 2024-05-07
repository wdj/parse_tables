#!/usr/bin/env python3
"""============================================================================

Various utilities used throughout the code.

============================================================================"""

import sys

# To install yaml do this: pip install PyYAML
import yaml

# Check Python version
if sys.version_info < (3, 7):
    sys.exit("This script requires Python 3.7 or higher"
             " (to support dict ordering guarantees)")

#------------------------------------------------------------------------------

#-----
# Define syntactic category codes.
#-----

"""
for the list of syntactic categories, see, e.g.,
ExecuteRules.cpp, lines 1362f
ExecuteRules.cpp, lines 2987f
ExecuteRules.cpp, lines 6512f
ExecuteRules.cpp, lines 11645f
ExecuteRules.cpp, lines 12313f
ExecuteRules.cpp, lines 21191f *
SystemDevelopmentView.cpp lines 6871f
"""

SYNTACTIC_CATEGORIES = {
         # ??? a setting of < 0 is a user-defined syntactic category ?
    'clitic':         '0', #   # ? clitic
    'noun':           '1', # N # Noun
    'verb':           '2', # V # Verb
    'adjective':      '3', # A # Adjective
    'adverb':         '4', # a # Adverb
    'adposition':     '5', # P # Adposition
    'conjunction':    '6', # C # Conjunction
   #'pronoun':        '7', # p # Pronoun # no longer allowed ?
    'phrasal':        '7', # p? # Phrasal
    'particle':       '8', # r # Particle
    'np':           '101', # n # NP
    'vp':           '102', # v # VP
    'adjp':         '103', # j # AdjP
    'advp':         '104', # d # AdvP
    'clause':       '105', # c # Clause
    'user-defined': '106', #   # user-defined
    'all':          '107', #   # all categories of words
    'paragraph':    '110', # R # paragraph
    'episode':      '120', # E # episode
}

SYNCATS = SYNTACTIC_CATEGORIES

#-----
# Helpers for subsets of syntactic categories.
#-----

def is_syncat_clause(syncat):
    return syncat == SYNCATS['clause']

def is_syncat_phrase(syncat):
    return syncat in [SYNCATS['np'], SYNCATS['vp'],
                      SYNCATS['adjp'], SYNCATS['advp']]

def is_syncat_word(syncat):
    return syncat in [SYNCATS['noun'], SYNCATS['verb'],
                      SYNCATS['adjective'], SYNCATS['adverb'],
                      SYNCATS['adposition'], SYNCATS['conjunction'],
                      SYNCATS['phrasal'], SYNCATS['particle']]

def is_syncat_topword(syncat):
    return syncat in [SYNCATS['noun'], SYNCATS['verb'],
                      SYNCATS['adjective'], SYNCATS['adverb']]

def is_syncat_bottomword(syncat):
    return syncat in [SYNCATS['adposition'], SYNCATS['conjunction'],
                      SYNCATS['phrasal'], SYNCATS['particle']]

#-----
# Misc. rule-specific definitions.
#-----

CLITIC_TYPES = [
    '0', # preclitic (proclitic)
    '1', # second position clitic
    '2', # postclitic (enclitic)
]

SPELLOUT_RULE_TYPES = {
    'Simple':                 '0',
    'Morphophonemic':         '1',
    'Lexical Form Selection': '2',
    'Table':                  '3',
    'Phrase Builder':         '4',
    'Suppletive Forms':       '5',
}

SPELLOUT_PREFIX_REDUP_NAMES = { **{
     '1': 'Reduplicate first character of stem.',
      }, **{
      str(i): f'Reduplicate first {i} characters of stem.'
        for i in range(2,9)}, **{
    '10': 'Reduplicate entire stem.',
    '11': 'Reduplicate entire stem with a hyphen.',
    '12': 'Reduplicate entire stem with a space.',
}}

SPELLOUT_SUFFIX_REDUP_NAMES = { **{
     '1': 'Reduplicate last character of stem.',
      }, **{
      str(i): f'Reduplicate last {i} characters of stem.'
        for i in range(2,9)}, **{
    '10': 'Reduplicate entire stem.',
    '11': 'Reduplicate entire stem with a hyphen.',
    '12': 'Reduplicate entire stem with a space.',
}}

SPELLOUT_PREFIX_MORPHO_REDUP_NAMES = {k: v for (k,v) in
                             list(SPELLOUT_PREFIX_REDUP_NAMES.items())[:10]}

SPELLOUT_SUFFIX_MORPHO_REDUP_NAMES = {k: v for (k,v) in
                             list(SPELLOUT_SUFFIX_REDUP_NAMES.items())[:10]}

SPELLOUT_INFIX_REDUP_NAMES = { **{
     '1': 'Reduplicate last character before marker.',
      }, **{
      str(i): f'Reduplicate last {i} characters before marker.'
        for i in range(2,9)}, **{
    '10': 'Reduplicate mll charcters before marker.',
    '11': 'Reduplicate first character after marker.',
      }, **{
      str(i): f'Reduplicate first {i} characters after marker.'
        for i in range(2,9)}, **{
    '10': 'Reduplicate mll charcters after marker.',
}}

SPELLOUT_MODIFICATION_SIMPLE_TABLE_TYPES = {
    'Prefix': '0',
    'Suffix': '1',
    'Infix': '2',
    'New translation': '3',
    'Add Word': '4',
    'Circumfix': '5',
}

SPELLOUT_MODIFICATION_MORPHOPHONEMIC_TYPES = {
    'prefix', '0',
    'infix, treated as prefix', '1',
    'infix, treated as suffix', '2',
    'suffix', '3',
    'circumfix, treated as prefix', '4',
    'circumfix, treated as suffix', '5',
}

SPELLOUT_BASEFORM_NAMES = [
    "Current entry",
    "Stem",
    "Citation Form",
]

SPELLOUT_BASEFORM_PHRASE_BUILDER_NAMES = SPELLOUT_BASEFORM_NAMES +  [
    "New Translation",
    "Delete Word",
]

#------------------------------------------------------------------------------

# Define codes for different rule types. Here, the name of the rule is simply
# the name of the associated .mdb table.
# Note this needs to be consistent with the codes used in Rules_Groups.
# It is tricky to infer sometimes what is the right code; below is best guess.
# Here, this is extended for "all" .mdb tables not just Rules_*.

RULE_TYPES = {
    #'Rules_ConstituentMovement' - seems obsolete
    'Rules_Lexical': '0', # CTA1Doc::GetRuleGroupName, CTA1Doc::GetNumberOfRules
    'Rules_FeatureCopying': '1', # CTA1Doc::UpdateRulesForNewCopiedFeature
    #'Rules_SourceAnalyzing': '2' # unused
        # ^^^CTA1Doc::GetRule, CTA1Doc::GetRulesSourceLanguage
    'Rules_TextPreprocessing': '3',
    'Rules_Spellout': '4', # CTA1Doc::UpdateRulesForNewFeature
    'Rules_WordMorphophonemic': '5', # CTA1Doc::UpdateRulesForNewFeature
    'Rules_Clitic': '6', # CTA1Doc::UpdateRulesForNewFeature
    'Rules_Movement': '7', # CTA1Doc::CheckMovementRulesSyntacticCategory
    'Rules_PhraseStructure': '8', # CTA1Doc::UpdateRulesForNewFeature
    'Rules_FindReplace': '9', # CTA1Doc::GetRule
    #'Rules_ComplexConcepts':  '10' # obsolete
        # ^^^ CTA1Doc::GetComplexConceptInsertionRulesThatApplyInThisVerse
    'Rules_Transfer': '10', # CTA1Doc::GetRule - lexical restructuring rules
    # lexical form selection - '11' # CTA1Doc::GetRule
    #'Rules_AffixHopping': '11', # obsolete
    'Rules_ThetaGridAdjustments': '12', # CTA1Doc::GetRule
    'Rules_PronounIdentification': '13', # CTA1Doc::UpdateRulesForNewFeature
    'Rules_PronounSpellout': '14', # CTA1Doc::GetRule
    'Rules_ComplexConcepts': '15', # CTA1Doc::GetRule, CTA1Doc::GetNumberOfRules
    'Rules_SpeechStyles': '16', # CTA1Doc::GetNumberOfRules
    #'Rules_FindReplace': '17', # CTA1Doc::GetNumberOfRules
        # ^^^ for source analyzer case ONLY
    #'Rules_FeatureSetting': '18', # CTA1Doc::GetNumberOfRules
    #'Rules_DeleteAmbiguousPOSTags': '19', # CTA1Doc::GetNumberOfRules
    # source analysis phrase structure rules '20' # CTA1Doc::GetRule
    'Rules_TenseAspectMood': '21', # CTA1Doc::GetNumberOfRules
    #'Rules_RelativizationRestructuring': '22',
        # ^^^ SelectRuleToEditDlg.cpp, line 478
    #'Rules_RelativizationRestructuring': '16', # CTA1Doc::SetRulesStatus
    #'Rules_RelativizationRestructuring': '21', # CTA1Doc::GetRulesReferences
    #'Rules_NounNounRelationshipRestructuring': '23',
        # ^^^ SelectRuleToEditDlg.cpp, line 479
    #'Rules_NounNounRelationshipRestructuring': '16'
        # ^^^ CTA1Doc::GetRulesReferences

    'Rules_FeatureCollapsing': '25',
    'Rules_RelativeClauses': '26',
    'Rules_RelativizationRestructuring': '27',
    'Rules_NounNounRelationshipRestructuring': '28',
    'Rules_NounNounRelationships': '29',
    'Rules_Groups': '30',

    'Adposition_Mappings_English': '41',
    'Conjunction_Mappings_English': '42',
    'Noun_Mappings_English': '43',
    'Particle_Mappings_English': '44',
    'Pronoun_Mappings_English': '45',
    'Adverb_Mappings_English': '46',
    'Verb_Mappings_English': '47',
    'Adjective_Mappings_English': '48',

    'Adjectives': '51',
    'Adpositions': '52',
    'Adverbs': '53',
    'Conjunctions': '54',
    'Nouns': '55',
    'Particles': '56',
    'Pronouns': '57',
    'Verbs': '58',

    'Source_UsersAdjectives': '61',
    'Source_UsersAdpositions': '62',
    'Source_UsersAdverbs': '63',
    'Source_UsersConjunctions': '64',
    'Source_UsersNouns': '65',
    'Source_UsersPronouns': '66',
    'Source_UsersVerbs': '67',
    'Source_UsersParticles': '68',

    'CharacterFeatureValues': '71',
    'PhoneticFeatures': '72',
    'Sorting_Sequence': '73',
    'Features_Source': '74',
    'Features_Target': '75',
    'LexicalFormNames': '76',

    'Ontology_Adjectives': '81',
    'Ontology_Adpositions': '82',
    'Ontology_Adverbs': '83',
    'Ontology_Conjunctions': '84',
    'Ontology_Nouns': '85',
    'Ontology_Particles': '86',
    'Ontology_Pronouns': '87',
    'Ontology_Verbs': '88',

    'Ontology_AdjectiveHierarchy': '91',
    'Ontology_AdpositionHierarchy': '92',
    'Ontology_AdverbHierarchy': '93',
    'Ontology_ConjunctionHierarchy': '94',
    'Ontology_NounHierarchy': '95',
    'Ontology_ParticleHierarchy': '96',
    'Ontology_PronounHierarchy': '97',
    'Ontology_VerbHierarchy': '92',

    'Ontology_Features_Source': '101',
    'Ontology_Sorting_Sequence': '102',
}

RULE_TYPES_ALL = {
    **RULE_TYPES,
     # The following not usually needed, but is used in Rules_Groups tables
     # for some languages.
    'Rules_AffixHopping': '11',
}

# Other attempts to determine rule type codes:

# ExecuteRules.h, lines 78f:
# enum eRuleType {
#ComplexConceptExpansion=0,
#FeatureCopying=1,
#SourceAnalysis=2,
#TextPreprocessors=3,
#Spellout=4,
#WordMorphophonemic=5,
#Clitic=6,
#Movement=7,
#PhraseStructure=8,
#FindReplace=9,
#Transfer=10,
#AffixHopping=11,
#ThetaGridAdjustment=12,
#PronounIdentification=13,
#PronounSpellout=14,
#ComplexConceptInsertion=15,
#NounNounRelationships=16,
#RelativeClauseRestructuring=17,
#SourceAnalysisPhraseStructure=20

#RULE_TYPES = {
#  'LexicalSpellout': 0, # ? text preprocessing
#  'Agreement': 1, # = feature copying
#  #'CollocationCorrection': 2, # (obsolete)
#  'Transfer': 3,
#  'Spellout': 4,
#  'WordMorphophonemic': 5,
#  'Clitics': 6,
#  'ConstituentMovement': 7,
#  'PhraseStructure': 8,
#  'FindReplace': 9,
#  'LexicalRestructuring': 10,
#  #'AffixHopping': 11, # (obsolete)
#  'ThetaGridAdjustment': 12,
#  'PronounIdentification': 13, # = Pronoun and Switch Reference Identification
#  'PronounSpellout': 14, # = Pronoun and Switch Reference Spellout
#  'ComplexConcepts': 15,
#  'Relative Clause Strategies': 21,
#  'Relative Clause Restructuring': 22,
#  'Noun-Noun Relationship Restructuring': 23,
#}

#------------------------------------------------------------------------------

def delim_rule_type(rule_type):
    """A delimiter used by Input/OutputStructures."""
    return '>|<' if (rule_type ==
        RULE_TYPES['Rules_FeatureCopying'])  else '-*-'

#------------------------------------------------------------------------------

# TA1Doc.cpp: GetSyntacticAbbreviation

#==============================================================================
