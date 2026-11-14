"""Fast Downward PDDL planner subprocess wrapper."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from planning.src.pddl_generator import DEFAULT_DOMAIN_PATH, DEFAULT_PROBLEM_PATH, PLANNING_DIR

DEFAULT_OUTPUT_DIR = PLANNING_DIR / "output"


def run_planner(
    domain_path: str | Path = DEFAULT_DOMAIN_PATH,
    problem_path: str | Path = DEFAULT_PROBLEM_PATH,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    planner_bin: str = "fast-downward",
) -> tuple[int, str]:
    """Run Fast Downward A* + LM-Cut on the generated domain and problem files."""
    domain_file = Path(domain_path).resolve()
    problem_file = Path(problem_path).resolve()
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    plan_path = out_dir / "plan.soln"
    sas_path = out_dir / "output.sas"
    log_path = out_dir / "plan.txt"
    for artifact in (plan_path, sas_path):
        if artifact.exists():
            artifact.unlink()

    # Keep all paths inside a single working root so containerized fast-downward
    # (which bind-mounts $PWD) can resolve domain, problem, and output files.
    work_root = out_dir.parent
    if domain_file.is_relative_to(work_root) and problem_file.is_relative_to(work_root):
        cwd = work_root
        domain_arg = str(domain_file.relative_to(work_root))
        problem_arg = str(problem_file.relative_to(work_root))
        plan_arg = str(plan_path.relative_to(work_root))
        sas_arg = str(sas_path.relative_to(work_root))
    else:
        cwd = out_dir
        staged_domain = out_dir / "domain.pddl"
        staged_problem = out_dir / "problem.pddl"
        shutil.copyfile(domain_file, staged_domain)
        shutil.copyfile(problem_file, staged_problem)
        domain_arg = staged_domain.name
        problem_arg = staged_problem.name
        plan_arg = plan_path.name
        sas_arg = sas_path.name

    cmd = [
        planner_bin,
        "--plan-file",
        plan_arg,
        "--sas-file",
        sas_arg,
        domain_arg,
        problem_arg,
        "--search",
        "astar(lmcut())",
    ]

    try:
        result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        log_path.write_text(f"Planner binary '{planner_bin}' not found: {exc}\n", encoding="utf-8")
        return 127, ""

    log_text = result.stdout
    if result.stderr:
        log_text = f"{log_text}\n{result.stderr}" if log_text else result.stderr
    log_path.write_text(log_text, encoding="utf-8")

    plan_text = plan_path.read_text(encoding="utf-8") if plan_path.exists() else ""
    return result.returncode, plan_text
