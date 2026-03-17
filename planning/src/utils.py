def parse_plan(raw_output):
    plan = []
    for line in raw_output.splitlines():
        tokens = line.strip().lower()
        if not tokens or tokens.startswith(("info", "[", ";")):
            continue

        if ":" in tokens and tokens.split(":")[0].isdigit():
            tokens = tokens.split(":", 1)[1].strip()

        if tokens.startswith("(") and tokens.endswith(")"):
            tokens = tokens[1:-1]

        parts = tokens.split()
        if not parts:
            continue

        last = parts[-1]
        if last.startswith("(") and last.endswith(")") and last[1:-1].isdigit():
            parts = parts[:-1]

        if parts:
            plan.append(parts)

    return plan
