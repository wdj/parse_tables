#!/usr/bin/env python3
"""============================================================================

Handle Rules_TenseAspectMood table from <MyLanguage>.mdb file.

============================================================================"""

import _utils
from rules_speech_styles import RulesSpeechStyles

#==============================================================================

class RulesTenseAspectMood(RulesSpeechStyles):
    """
    Handle Rules_TenseAspectMood table from <MyLanguage>.mdb file.

    Most functionality is provided by base class.

    -----------------------------------------------------------------------
    Notes

    see CExecuteRules::ExecuteTenseAspectMoodRules
    see CTA1Doc::GetTAMRule

    It would seem this is different from Rules_SpeechStyles only insofar as
    InputFeatures doesn't have the last field.

    -----------------------------------------------------------------------
    """

    RULE_TYPE = _utils.RULE_TYPES['Rules_TenseAspectMood']

#==============================================================================
