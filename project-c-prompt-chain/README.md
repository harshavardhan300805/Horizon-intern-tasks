# Complex Prompt Chain for Research & Data Synthesis — Prompt Engineering Project C

A 4-stage prompt chain that turns a broad research topic into a structured,
critiqued, and synthesized report — demonstrating chained prompting instead
of one large "do everything" prompt.

## Why a chain instead of one prompt?

Asking a single prompt to "research and write a report on X" tends to
produce shallow, generic output. This project decomposes that task into
four narrow, single-purpose stages, each with its own system prompt, where
each stage's output becomes the next stage's input:

```
Topic
  │
  ▼
[1] Decompose  ──► 3-5 focused sub-questions
  │
  ▼
[2] Research   ──► each sub-question answered independently (no cross-talk)
  │
  ▼
[3] Critique   ──► flags contradictions, vague claims, and gaps
  │
  ▼
[4] Synthesize ──► final Markdown report that addresses the critique
```

Because each stage only sees what it needs, the sub-answers stay focused,
and the critique stage catches issues before they reach the final report —
something a single monolithic prompt has no mechanism to do.

## Project structure

```
project-c-prompt-chain/
├── chain.py          # Core chain logic: 4 stages + demo mode
├── run.py             # CLI entry point
├── requirements.txt
└── README.md
```

## Running it

### Demo mode (no API key needed)

```bash
pip install -r requirements.txt
python run.py --demo "Prompt engineering for autonomous agents"
```

Runs the full 4-stage structure with placeholder answers so the chain's
shape is visible without API calls — useful for the required
screenshots/video.

### Live mode

```bash
export ANTHROPIC_API_KEY=your_key_here
python run.py "Prompt engineering for autonomous agents"
```

Every run also writes `chain_output.json`, containing the full trace
(sub-questions, each sub-answer, the critique notes, and the final report)
so the intermediate reasoning is inspectable, not just the final text.

## Example output (demo mode)

```
# Research Report: Prompt engineering for autonomous agents

## Introduction
Brief framing of the topic and why it matters.

## What problem does it solve?
...

## Current approaches
...

## Limitations
... (Note: a concrete example should be added — flagged by the critique stage.)

## Outlook
... This is speculative, as flagged by the critique stage.

## Conclusion
...
```

## What I'd extend next

- Give the Research stage (Stage 2) real web-search tool access instead of
  relying on the model's own knowledge
- Let the Critique stage trigger a second Research pass to fill gaps it finds,
  instead of just flagging them for Synthesis to mention
- Add a lightweight scoring rubric to automatically evaluate report quality
  across multiple runs
