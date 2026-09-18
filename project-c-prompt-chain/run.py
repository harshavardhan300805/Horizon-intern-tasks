"""
run.py
------
Simple CLI wrapper around chain.py.

Usage:
    python run.py "Your research topic here"
    python run.py --demo "Your research topic here"   # force demo mode
"""

import argparse
import json
import os

from chain import run_chain, run_chain_demo


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the research/data synthesis prompt chain")
    parser.add_argument("topic", nargs="+", help="Research topic")
    parser.add_argument("--demo", action="store_true", help="Force scripted demo mode (no API key needed)")
    args = parser.parse_args()

    topic = " ".join(args.topic)

    if args.demo or not os.environ.get("ANTHROPIC_API_KEY"):
        if not args.demo:
            print("[No ANTHROPIC_API_KEY found — running demo mode]\n")
        result = run_chain_demo(topic)
    else:
        print(f"Running chain on: {topic}\n")
        result = run_chain(topic)

    print("=" * 60)
    print(" FINAL REPORT")
    print("=" * 60)
    print(result.final_report)

    with open("chain_output.json", "w") as f:
        json.dump(result.to_dict(), f, indent=2)
    print("\n[Full chain trace — sub-questions, sub-answers, critique — written to chain_output.json]")


if __name__ == "__main__":
    main()
