"""Interview follow-up prompt builder (interview-specific, not platform kernel)."""
from __future__ import annotations

from typing import Any, Dict, List

from models.interview import InterviewType
from services.interview.session.runtime.question_text import extract_question_text


def build_follow_up_prompt(
    previous_qa: List[Dict[str, Any]],
    interview_type: InterviewType,
    llm_context: str,
) -> str:
    last_pairs = previous_qa[-4:]
    conversation_parts = []
    for qa in last_pairs:
        q_entry = qa.get("question", {})
        q_text = extract_question_text(q_entry)
        a_text = qa.get("response", "")
        conversation_parts.append(f"Interviewer: {q_text}\nCandidate: {a_text[:500]}")
    conversation = "\n\n".join(conversation_parts) or "Interviewer: Let's begin.\nCandidate: (no response yet)"
    interview_type_str = interview_type.value if isinstance(interview_type, InterviewType) else str(interview_type)
    context_block = llm_context.strip() or f"INTERVIEW TYPE: {interview_type_str}\nCONVERSATION SO FAR:\n{conversation}"
    resume_mode_rule = ""
    if interview_type == InterviewType.RESUME_BASED:
        resume_mode_rule = (
            "\nResume deep-dive mode:\n"
            "- Every question must trace to a specific resume claim.\n"
            "- Probe metrics, constraints, ownership, and tradeoffs before moving on.\n"
            "- If an answer is vague, ask a tighter follow-up on that same claim."
        )

    return f"""SYSTEM PROMPT FOR INTERVIEWER LLM:

You are a senior software engineer conducting a real technical interview.
You are not a question dispenser. You are a person having a conversation.

Your personality:
- Curious and direct. You ask because you genuinely want to understand.
- Patient but not passive. If an answer is incomplete, you probe.
- You push harder when someone is doing well. You back off when they're lost.
- You occasionally say "hmm" or pause. You're thinking too.
- You never say "Great answer!" or "Excellent!" - it sounds fake.
  Instead: "Right.", "Okay, that makes sense.", "Interesting." or nothing.
- You reference things said earlier. You remember the whole conversation.
- When the candidate is coding, you acknowledge what you see on screen.

Your one rule:
Always react to what was JUST said before asking anything new.
Never jump to the next question without acknowledging the last answer.
Even a single word ("Right.") is enough. Never skip this.

THE CONTEXT BELOW IS YOUR REALITY. Trust it completely.
Adapt everything you say to what it tells you about this candidate right now.
{resume_mode_rule}

{context_block}

RECENT DIALOGUE:
{conversation}

Now respond as the interviewer. One focused thing at a time."""
