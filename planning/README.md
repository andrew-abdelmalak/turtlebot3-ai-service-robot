Apartment planning playground built around Fast Downward. The code models a small apartment, converts goals entered in a CLI into PDDL, calls the Fast Downward planner to solve them, and steps through the resulting plan while updating an in-memory knowledge base.

## Repository layout
- `src/`: Python code for the CLI and PDDL plumbing.
  - `main.py`: Boots the world model, knowledge base, and CLI loop.
  - `world_model.py`: Static description of rooms, connectivity, and initial object placement.
  - `kb.py`: Knowledge base holding the robot location, held object, and object locations; can apply executed actions.
  - `pddl_generator.py`: Emits the PDDL domain (`domain/domain.pddl`) and problem (`problems/problem.pddl`) from Python each run based on the current KB and a user-specified goal.
  - `planner.py`: Shells out to `fast-downward` with the generated problem, captures `output/plan.soln` and logs `output/plan.txt`.
  - `utils.py`: Plan text parsing helpers.
  - `cli.py`: Text UI to accept goals (`robot-at <room>`, `at <object> <room>`, `holding <object>`), run the planner, display, and apply the plan.
- `domain/domain.pddl`: Domain definition with `move`, `pick`, and `place` actions (generated automatically).
- `problems/problem.pddl`: Sample problem; rewritten on each CLI run.
- `output/`: Planner artifacts (`plan.soln`, `plan.txt`, and the latest `sas_plan` if produced).
- `downward/`: Vendored Fast Downward source; use its README to build/install the `fast-downward` binary.
- `milestone_description/`, `report/`: Assignment brief and submitted report (PDF + assets).

## Requirements
- Python 3.8+.
- Fast Downward available as `fast-downward` on your `PATH` (or adjust `src/planner.py` to point at `downward/fast-downward.py`).

## Running
1. (Optional) Build Fast Downward in `downward/` following `downward/README.md`, then add the produced `fast-downward` wrapper/binary to your `PATH`.
2. From the repo root: `python src/main.py`
3. At the prompt, enter goals such as:
   - `robot-at kitchen`
   - `at cup bedroom`
   - `(holding phone)`
4. Plans and logs appear in `output/plan.soln` and `output/plan.txt`; the KB state shown in the CLI updates as each action is applied.
