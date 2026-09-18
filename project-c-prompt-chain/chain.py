"""
chain.py
--------
A 4-stage prompt chain for research & data synthesis.

Stage 1 — Decompose: break a broad topic into focused sub-questions.
Stage 2 — Research each sub-question: answer it in isolation (each call
          only sees its own sub-question, forcing focused, non-redundant
          output).
Stage 3 — Critique: a separate pass reviews the Stage 2 answers for gaps,
          contradictions, or unsupported claims before synthesis.
Stage 4 — Synthesize: combine sub-answers + critique notes into one
          coherent research report.

Each stage is a distinct system prompt with a narrow job, and each stage's
output becomes the next stage's input — that's the "chain" being
engineered here, as opposed to one big prompt asking for everything at once.
"""

import json
import os
from dataclasses import dataclass, field

MODEL = "claude-sonnet-4-5"


@dataclass
class ChainResult:
    topic: str
    sub_questions: list[str] = field(default_factory=list)
    sub_answers: dict[str, str] = field(default_factory=dict)
    critique: str = ""
    final_report: str = ""

    def to_dict(self):
        return {
            "topic": self.topic,
            "sub_questions": self.sub_questions,
            "sub_answers": self.sub_answers,
            "critique": self.critique,
            "final_report": self.final_report,
        }


# ---------------------------------------------------------------------------
# System prompts for each stage (kept narrow and single-purpose on purpose)
# ---------------------------------------------------------------------------

DECOMPOSE_SYSTEM = (
    "You are a research planner. Given a broad topic, break it into 3 to 5 "
    "focused, non-overlapping sub-questions that together give a well-rounded "
    "understanding of the topic. Respond ONLY with a JSON array of strings, "
    "no other text."
)

RESEARCH_SYSTEM = (
    "You are a focused research assistant. Answer ONLY the specific "
    "sub-question you are given, in 3-5 sentences, in a neutral analytical "
    "tone. Do not reference other sub-questions. If you are uncertain about "
    "a fact, say so explicitly rather than guessing."
)

CRITIQUE_SYSTEM = (
    "You are an editorial critic reviewing draft research notes before they "
    "are published. Identify: (1) any contradictions between notes, (2) any "
    "unsupported or vague claims, (3) any important gaps. Be concise — "
    "output a short bulleted list, not prose paragraphs."
)

SYNTHESIZE_SYSTEM = (
    "You are a research writer. Combine the provided sub-answers and "
    "critique notes into one coherent, well-organized report with a short "
    "introduction, a section per sub-question, and a brief conclusion. "
    "Address the critique notes where relevant (e.g. flag remaining "
    "uncertainty rather than ignoring it). Use Markdown."
)


def _call(client, system: str, user: str) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=800,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in response.content if block.type == "text")


def run_chain(topic: str, client=None) -> ChainResult:
    """Run the full 4-stage chain against the live Anthropic API."""
    import anthropic

    client = client or anthropic.Anthropic()
    result = ChainResult(topic=topic)

    # Stage 1: decompose
    raw = _call(client, DECOMPOSE_SYSTEM, f"Topic: {topic}")
    result.sub_questions = json.loads(raw)

    # Stage 2: research each sub-question independently
    for q in result.sub_questions:
        result.sub_answers[q] = _call(client, RESEARCH_SYSTEM, q)

    # Stage 3: critique the collected answers
    notes_blob = "\n\n".join(f"Q: {q}\nA: {a}" for q, a in result.sub_answers.items())
    result.critique = _call(client, CRITIQUE_SYSTEM, notes_blob)

    # Stage 4: synthesize final report
    synth_input = (
        f"Topic: {topic}\n\nSub-answers:\n{notes_blob}\n\nCritique notes:\n{result.critique}"
    )
    result.final_report = _call(client, SYNTHESIZE_SYSTEM, synth_input)

    return result


# ---------------------------------------------------------------------------
# Demo mode: a scripted run so the chain's structure is visible without an
# API key (used for the required screenshots / video).
# ---------------------------------------------------------------------------

def run_chain_demo(topic: str) -> ChainResult:
    result = ChainResult(topic=topic)
    result.sub_questions = [
        f"What problem does {topic} solve, and for whom?",
        f"What are the main technical approaches used in {topic} today?",
        f"What are the current limitations or open challenges in {topic}?",
        f"Where is {topic} likely headed in the next few years?",
    ]
    result.sub_answers = {
        result.sub_questions[0]: (
            "[demo answer] Summarizes the core problem and primary users, based on this "
            "sub-question in isolation."
        ),
        result.sub_questions[1]: (
            "[demo answer] Summarizes the 2-3 dominant technical approaches, noting "
            "trade-offs between them."
        ),
        result.sub_questions[2]: (
            "[demo answer] Lists the most commonly cited open challenges or limitations."
        ),
        result.sub_questions[3]: (
            "[demo answer] Offers a cautious, near-term outlook, flagging genuine uncertainty."
        ),
    }
    result.critique = (
        "- No major contradictions found between sub-answers.\n"
        "- The 'limitations' answer is somewhat vague — needs a concrete example.\n"
        "- The 'future direction' answer should explicitly flag it is speculative."
    )
    result.final_report = (
        f"# Research Report: {topic}\n\n"
        f"## Introduction\n[demo] Brief framing of {topic} and why it matters.\n\n"
        f"## What problem does it solve?\n{result.sub_answers[result.sub_questions[0]]}\n\n"
        f"## Current approaches\n{result.sub_answers[result.sub_questions[1]]}\n\n"
        f"## Limitations\n{result.sub_answers[result.sub_questions[2]]} "
        f"(Note: a concrete example should be added — flagged by the critique stage.)\n\n"
        f"## Outlook\n{result.sub_answers[result.sub_questions[3]]} "
        f"This is speculative, as flagged by the critique stage.\n\n"
        f"## Conclusion\n[demo] Short wrap-up synthesizing the sections above.\n"
    )
    return result


if __name__ == "__main__":
    import sys

    topic = " ".join(sys.argv[1:]) or "Prompt engineering for autonomous agents"
    if os.environ.get("ANTHROPIC_API_KEY"):
        result = run_chain(topic)
    else:
        print("[No ANTHROPIC_API_KEY found — running demo mode]\n")
        result = run_chain_demo(topic)

    print(result.final_report)
    with open("chain_output.json", "w") as f:
        json.dump(result.to_dict(), f, indent=2)
    print("\n[Full chain trace written to chain_output.json]")
