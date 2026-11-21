"""Scores an interview thread on English, content, and (from the audio) speaking."""

import base64
import os

from pydantic import BaseModel, Field

from .background import candidate_background
from .llm import complete, format_interview, parse_json_reply

Score = Field(ge=0, le=100)


def feedback_language() -> str:
    """The language to write feedback in: FEEDBACK_LANGUAGE, else English."""
    return os.environ.get("FEEDBACK_LANGUAGE", "").strip() or "English"


class Correction(BaseModel):
    original: str = Field(description="A phrase or sentence the candidate said, quoted as-is.")
    improved: str = Field(description="A more correct or natural way to say it.")
    explanation: str = Field(description="Why the improved version is better.")


class EnglishFeedback(BaseModel):
    grammar: int = Score
    vocabulary: int = Score
    naturalness: int = Score
    summary: str
    corrections: list[Correction] = Field(max_length=5)


class ContentFeedback(BaseModel):
    relevance: int = Score
    structure: int = Score
    specificity: int = Score
    summary: str
    strengths: list[str] = Field(max_length=3)
    improvements: list[str] = Field(max_length=3)


class Feedback(BaseModel):
    english: EnglishFeedback
    content: ContentFeedback
    better_answer: str = Field(
        description="The candidate's answer to the first question, rewritten in English."
    )


SYSTEM_PROMPT = """\
You are an interview coach reviewing a mock job interview held in English. The candidate
is a non-native English speaker practicing for real interviews. You will get the questions
and the candidate's answers. The answers are speech-recognition transcripts: ignore missing
punctuation and capitalization, and do not count an obvious recognition error (a word that
makes no sense where a similar-sounding word would) against the candidate.

Evaluate two things separately, so a good story told in weak English and fluent English
with nothing to say get different scores.

English (the sentences only; pronunciation is measured separately from the audio):
- grammar: tense, agreement, articles, prepositions, sentence construction.
- vocabulary: precise and varied word choice suited to a professional interview.
- naturalness: how close the phrasing is to what a fluent professional would say aloud.
- corrections: up to five of the most valuable fixes, most important first. Quote what the
  candidate said, give the better version, and explain why. Use an empty list if there is
  nothing worth fixing.

Content (what was said, regardless of the English):
- relevance: whether each answer addresses the question that was asked. If a job posting
  is given, also whether the answer speaks to what that role needs.
- structure: a clear, easy-to-follow line, e.g. situation, action, result, without rambling.
- specificity: concrete details, such as the candidate's own role, decisions, numbers, and
  outcomes, rather than generic claims.
- strengths and improvements: up to three each, tied to what was actually said.

The message may start with the job posting the candidate is preparing for, their résumé,
and their cover letter. Use them as background: point out relevant experience from the
résumé or cover letter that the candidate left out, and draw on it (never on invented experience) in better_answer.

Scores are integers from 0 to 100. Calibrate them honestly, because an inflated score hides
what to practice: 90+ would impress in a real interview, 75-89 is solid with minor issues,
60-74 gets the point across with clear weaknesses, 40-59 is hard to follow or thin, and
below 40 mostly fails to communicate or to answer. A very short answer cannot score high
on structure or specificity.

better_answer: rewrite the candidate's answer to the first question as a strong spoken
answer of about 80-130 words in natural English. Keep their facts and do not invent
experience; where a detail such as a number is missing, leave a bracketed placeholder
like [metric] for them to fill in.

Write summary, explanation, strengths, and improvements in {language}. Keep "original",
"improved", and better_answer in English. Summaries are two or three sentences.

Reply with a single JSON object matching this schema, and nothing else:
{schema}"""


def evaluate(turns: list[tuple[str, str]], question_id: int | None = None) -> Feedback:
    """Return English and content feedback for the (question, answer) turns of a saved question."""
    language = feedback_language()
    system = SYSTEM_PROMPT.format(language=language, schema=Feedback.model_json_schema())
    reply = complete(
        system,
        format_interview(turns, candidate_background(question_id)),
        max_tokens=8000,
        response_format={"type": "json_object"},
    )
    return parse_json_reply(reply, Feedback)


class SpeakingTip(BaseModel):
    phrase: str = Field(description="The word or short phrase from the answer, in English.")
    advice: str = Field(description="What was off and how to say it.")


class SpeakingFeedback(BaseModel):
    pronunciation: int = Score
    intonation: int = Score
    stress: int = Score
    summary: str
    tips: list[SpeakingTip] = Field(max_length=5)


SPEAKING_PROMPT = """\
You are an English pronunciation coach. You will hear a non-native speaker answering
mock job interview questions in English, one audio clip per answer, each with the question
and a machine transcript for reference. Judge only how the answers sound; grammar, word
choice, and content are evaluated elsewhere. Base every judgement on the audio itself, not
on the transcript, which may be wrong where the speech was unclear.

Score three things:
- pronunciation: how accurately individual sounds are produced (vowels, consonants, word
  endings), and how easily a native listener would understand each word.
- intonation: whether pitch rises and falls naturally, e.g. falling at the end of
  statements and varying to mark important information, rather than flat or sing-song.
- stress: correct syllable stress within words, emphasis on the content words of a
  sentence, and a natural rhythm as a result.

tips: up to five specific things to practice, most valuable first. Name the exact word or
phrase from the audio and say what was off and how to say it, e.g. which syllable to
stress. Use an empty list if nothing stands out. Do not invent problems you did not hear.

Scores are integers from 0 to 100, calibrated honestly: 90+ is near-native and effortless
to follow, 75-89 is clearly understandable with a noticeable accent, 60-74 takes some
effort to follow in places, 40-59 is often hard to understand, and below 40 is mostly
unintelligible. An accent alone is not a fault; what matters is how easily the speaker is
understood and how natural the melody and rhythm sound.

Write summary and advice in {language}; keep "phrase" in English. The summary is two or
three sentences.

Reply with a single JSON object matching this schema, and nothing else:
{schema}"""


def evaluate_speaking(clips: list[tuple[str, str, bytes]]) -> SpeakingFeedback:
    """Score pronunciation, intonation, and stress from (question, transcript, wav) clips.

    Needs a model that accepts audio input (e.g. Gemini); other models raise LLMError.
    """
    language = feedback_language()
    system = SPEAKING_PROMPT.format(language=language, schema=SpeakingFeedback.model_json_schema())
    parts: list[dict] = []
    for number, (question, transcript, wav) in enumerate(clips, start=1):
        parts.append(
            {
                "type": "text",
                "text": f"Answer {number}\nQuestion: {question}\nMachine transcript: {transcript}",
            }
        )
        parts.append(
            {
                "type": "input_audio",
                "input_audio": {"data": base64.b64encode(wav).decode(), "format": "wav"},
            }
        )
    reply = complete(
        system,
        parts,
        max_tokens=8000,
        response_format={"type": "json_object"},
        # Audio takes longer to upload and process than text.
        timeout=90,
    )
    return parse_json_reply(reply, SpeakingFeedback)
