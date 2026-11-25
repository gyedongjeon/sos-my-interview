"""Generates interview questions tailored to a job posting (and the résumé, if any)."""

from typing import Literal

from pydantic import BaseModel, Field

from .levels import asking_guide
from .llm import complete, parse_json_reply

QUESTION_COUNT = 8

Difficulty = Literal["easy", "standard", "hard"]

DIFFICULTY_GUIDE: dict[str, str] = {
    "easy": (
        "Difficulty: easy. These are warm-up questions for someone still building confidence in "
        "English. Each question is one short sentence of at most 15 words, asks about one thing "
        "only, and uses everyday words. Ask about experience and opinions the candidate can "
        "answer from memory (\"What did you do...\", \"How do you usually...\"), not about "
        "designing systems or weighing trade-offs."
    ),
    "standard": (
        "Difficulty: standard. Each question is one sentence of at most 25 words and asks one "
        "thing, with no second part joined by \"and\" or a semicolon. Do not put a lead-in "
        "clause about the candidate's background or the company before the question. Ask what "
        "a friendly first-round interviewer would: real, relevant, and answerable in two minutes "
        "without deep preparation."
    ),
    "hard": (
        "Difficulty: hard. Ask the demanding questions of a final-round interview: scenarios "
        "with constraints, trade-offs, and failure cases specific to this role. A question may "
        "be two sentences, but it still asks one thing."
    ),
}


class TailoredQuestions(BaseModel):
    questions: list[str] = Field(min_length=1, max_length=QUESTION_COUNT)


SYSTEM_PROMPT = """\
You are the hiring manager preparing a first-round interview, held in English, for the job
posting below. Write the {count} questions you would actually ask this candidate, so they
can rehearse the real interview.

Cover the interview the way it usually runs, in this order:
- one or two on motivation and fit: why this company and this role in particular;
- three or four on the role's core requirements: technical or domain questions that test
  the skills and responsibilities the posting stresses, asked the way an interviewer
  would aloud (no coding exercises or anything that needs a whiteboard);
- two or three behavioral questions on the situations this role will face, such as
  ownership, conflict, incidents, or deadlines, phrased as "Tell me about a time...".

If a résumé is given, make some of the questions about it: ask about a specific project,
role, or claim on it that matters for this job, and probe any gap between the résumé and
what the posting requires. If there is no résumé, keep the questions about the role.
If a cover letter is given, ask about a claim or motivation the candidate wrote in it, the
way an interviewer who has read it would.

{difficulty}

{level}Name the company or the role only where it is natural. Write plain spoken English with no
numbering or labels, because each question is read aloud as-is.
Do not include generic questions that fit any job, such as "Tell me about yourself" or
"What are your strengths?"; the candidate already practices those separately.

Reply with a single JSON object matching this schema, and nothing else:
{schema}"""


def generate_questions(
    title: str,
    posting: str,
    resume: str | None,
    cover_letter: str | None = None,
    difficulty: Difficulty = "standard",
) -> list[str]:
    """Return interview questions for a posting. Raises LLMError when the model fails."""
    system = SYSTEM_PROMPT.format(
        count=QUESTION_COUNT,
        difficulty=DIFFICULTY_GUIDE[difficulty],
        level=asking_guide(),
        schema=TailoredQuestions.model_json_schema(),
    )
    user = f"<job_posting title={title!r}>\n{posting}\n</job_posting>"
    if resume:
        user += f"\n\n<resume>\n{resume}\n</resume>"
    if cover_letter:
        user += f"\n\n<cover_letter>\n{cover_letter}\n</cover_letter>"
    reply = complete(
        system, user, max_tokens=8000, response_format={"type": "json_object"}, timeout=60
    )
    questions = parse_json_reply(reply, TailoredQuestions).questions
    return [q.strip() for q in questions if q.strip()]
