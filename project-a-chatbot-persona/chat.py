"""
chat.py
-------
CLI entry point for the Custom Chatbot Persona project.

Usage:
    python chat.py                 # interactive persona picker
    python chat.py --persona coach # jump straight into a persona
    python chat.py --demo          # run a scripted demo, no API key required

Requires the ANTHROPIC_API_KEY environment variable to talk to the real
model. Without it (or with --demo), the script runs a scripted demo
conversation so you can still see the persona design and take screenshots.
"""

import argparse
import os
import sys

from personas import PERSONAS, get_persona, list_personas

MODEL = "claude-sonnet-4-5"


def print_banner(persona) -> None:
    print("=" * 60)
    print(f" {persona.display_name}")
    print("=" * 60)
    print(persona.greeting)
    print("(type 'exit' to quit, 'switch' to change persona)\n")


def choose_persona_interactively():
    personas = list_personas()
    print("Available personas:\n")
    for i, p in enumerate(personas, start=1):
        print(f"  {i}. {p.display_name}")
    while True:
        choice = input("\nPick a persona (number): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(personas):
            return personas[int(choice) - 1]
        print("Invalid choice, try again.")


def run_demo(persona) -> None:
    """Scripted conversation, useful for screenshots/video without an API key."""
    print_banner(persona)
    demo_turns = {
        "mentor": [
            ("I have an idea for an app but no users yet. Where do I start?",
             "Good — ideas are cheap, validated problems are gold. This week: talk to 10 people who "
             "have the problem you think you're solving, and just listen. Don't pitch, don't build yet.\n"
             "Next action: book those 10 conversations before Friday."),
        ],
        "tutor": [
            ("Can you just tell me how to solve 2x + 4 = 10?",
             "Let's get there together. What operation would undo the '+4' on the left side?"),
        ],
        "coach": [
            ("I want to start working out but I've never lifted weights before.",
             "Love that you're starting! Quick check first — any injuries or joint issues I should know about?"),
        ],
    }
    for user_msg, reply in demo_turns.get(persona.key, []):
        print(f"You: {user_msg}")
        print(f"{persona.display_name.split(' (')[0]}: {reply}\n")
    print("[demo mode — connect ANTHROPIC_API_KEY for a live conversation]")


def run_live(persona) -> None:
    try:
        import anthropic
    except ImportError:
        print("The 'anthropic' package is not installed. Run: pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
    history = []
    print_banner(persona)

    while True:
        user_msg = input("You: ").strip()
        if user_msg.lower() == "exit":
            break
        if user_msg.lower() == "switch":
            persona = choose_persona_interactively()
            history = []
            print_banner(persona)
            continue

        history.append({"role": "user", "content": user_msg})
        response = client.messages.create(
            model=MODEL,
            max_tokens=400,
            system=persona.system_prompt,
            messages=history,
        )
        reply_text = "".join(
            block.text for block in response.content if block.type == "text"
        )
        print(f"{persona.display_name.split(' (')[0]}: {reply_text}\n")
        history.append({"role": "assistant", "content": reply_text})


def main() -> None:
    parser = argparse.ArgumentParser(description="Custom Chatbot Persona demo")
    parser.add_argument("--persona", choices=list(PERSONAS.keys()), help="Persona key to use")
    parser.add_argument("--demo", action="store_true", help="Run a scripted demo, no API key needed")
    args = parser.parse_args()

    persona = get_persona(args.persona) if args.persona else choose_persona_interactively()

    if args.demo or not os.environ.get("ANTHROPIC_API_KEY"):
        run_demo(persona)
    else:
        run_live(persona)


if __name__ == "__main__":
    main()
