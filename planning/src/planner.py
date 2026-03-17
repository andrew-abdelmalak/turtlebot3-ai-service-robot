import subprocess
from pathlib import Path


def run_planner():
    plan_path = Path("output/plan.soln")
    if plan_path.exists():
        plan_path.unlink()

    cmd = [
        "fast-downward",
        "--plan-file",
        str(plan_path),
        "domain/domain.pddl",
        "problems/problem.pddl",
        "--search",
        "astar(lmcut())",
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    log_path = output_dir / "plan.txt"
    log_text = result.stdout
    if result.stderr:
        log_text += "\n" + result.stderr
    log_path.write_text(log_text)

    plan_text = plan_path.read_text() if plan_path.exists() else ""
    return result.returncode, plan_text
