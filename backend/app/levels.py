"""What the prompts are told about the user's English level (a CEFR level chosen under Settings).

The level changes the English the model writes for the user to say or to understand by ear; it
never changes how answers are scored, so scores stay comparable over time.
"""

from .settings import english_level

# The level a better sentence may reach: one step above the user's, to grow into.
NEXT = {"A2": "B1", "B1": "B2", "B2": "C1", "C1": "C1"}


def writing_guide() -> str:
    """For feedback: better_answer and corrections at the level or one step above; "" without a level."""
    level = english_level()
    if not level:
        return ""
    reach = f"at level {level}" if NEXT[level] == level else f"at level {level}, or at most {NEXT[level]},"
    return (
        f"The candidate's English is at CEFR level {level}. Write better_answer and every "
        f'"improved" so that they can learn them and say them aloud themselves: {reach} in '
        "vocabulary and sentence structure. Prefer common words and clear sentences over idioms "
        "and rare words beyond that; where a fix would need a harder construction, give the "
        "simpler correct one. The level does not change the scores.\n\n"
    )


def asking_guide() -> str:
    """For questions read aloud: worded for the level; "" without a level."""
    level = english_level()
    if not level:
        return ""
    return (
        f"The candidate's English is at CEFR level {level}: word each question so that they "
        "understand it by ear the first time, with vocabulary and sentence structure at that "
        "level. This changes only the wording, not what is asked or how demanding it is.\n\n"
    )
