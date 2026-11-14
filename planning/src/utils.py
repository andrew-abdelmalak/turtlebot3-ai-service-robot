"""Plan output parser for Fast Downward solution files."""

from __future__ import annotations


def parse_plan(raw_output: str) -> list[list[str]]:
    """Parse Fast Downward plan text into a list of ``[action, *args]`` tokens."""
    plan: list[list[str]] = []
    for line in raw_output.splitlines():
        tokens = line.strip().lower()
        if not tokens or tokens.startswith(("info", "[", ";")):
            continue

        if ":" in tokens and tokens.split(":", 1)[0].isdigit():
            tokens = tokens.split(":", 1)[1].strip()

        # Strip trailing "(cost)" suffix before unwrapping "(action args...)".
        if tokens.endswith(")") and " (" in tokens:
            prefix, suffix = tokens.rsplit(" (", 1)
            if suffix[:-1].isdigit():
                tokens = prefix.strip()

        if tokens.startswith("(") and tokens.endswith(")"):
            tokens = tokens[1:-1]

        parts = tokens.split()
        if parts:
            plan.append(parts)

    return plan
