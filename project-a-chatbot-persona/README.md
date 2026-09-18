# Custom Chatbot Persona — Prompt Engineering Project A

A CLI chatbot with three distinct, engineered personas — a startup mentor, a
Socratic tutor, and a fitness coach — built to demonstrate how structured
system-prompt design (role, tone, expertise, style rules, guardrails)
changes a model's behavior even when the underlying model is identical.

## Why this project

Anyone can write "act like a fitness coach." This project treats the system
prompt as an engineered artifact: each persona is assembled from five
explicit components so the design decisions are visible, comparable, and
reusable (see `personas.py`).

## Project structure

```
project-a-chatbot-persona/
├── chat.py          # CLI entry point / conversation loop
├── personas.py       # Persona definitions + system prompt builder
├── requirements.txt
└── README.md
```

## Personas

| Persona | Role | Key behavior |
|---|---|---|
| Startup Mentor (Ravi) | Pragmatic startup advisor | Ends every answer with one concrete next action |
| Socratic Tutor (Prof. Iyer) | Patient tutor | Asks guiding questions before giving direct answers |
| Fitness Coach (Maya) | Certified fitness coach | Always checks for injuries before suggesting exercises |

## How the system prompt is built

Each persona's prompt is generated from five parts in `_build_system_prompt()`:

1. **Role** — who the model is playing
2. **Tone** — how it should sound
3. **Expertise** — its declared knowledge domain
4. **Style rules** — concrete behavioral rules (length limits, structure, etc.)
5. **Guardrails** — explicit things the persona must never do

This structure makes it easy to add a new persona (see `_register(...)` calls
at the bottom of `personas.py`) without rewriting prompt-writing logic.

## Running it

### Demo mode (no API key needed)

```bash
pip install -r requirements.txt
python chat.py --demo --persona mentor
```

Runs a short scripted conversation for each persona so you can see the
design without an API key — useful for the required screenshots/video.

### Live mode

```bash
export ANTHROPIC_API_KEY=your_key_here
python chat.py --persona tutor
```

Starts a live conversation with the chosen persona. Type `switch` to change
persona mid-session, or `exit` to quit.

## Example (demo mode)

```
============================================================
 Startup Mentor (Ravi)
============================================================
Hey, I'm Ravi — think of me as a startup mentor on call. What are you building?

You: I have an idea for an app but no users yet. Where do I start?
Ravi: Good — ideas are cheap, validated problems are gold. This week: talk
to 10 people who have the problem you think you're solving, and just listen.
Don't pitch, don't build yet.
Next action: book those 10 conversations before Friday.
```

## What I'd extend next

- Persistent conversation memory across sessions (currently in-memory only)
- A simple web UI instead of CLI
- Automated evaluation: same question sent to all personas, scored on
  how well each stays in character
