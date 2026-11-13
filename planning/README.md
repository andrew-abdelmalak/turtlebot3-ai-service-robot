# Planning Layer

Standalone PDDL planning and closed-loop execution package built around Fast Downward (`astar(lmcut())`).

## Layout

- `src/main.py`: CLI entry point (`tb3-planner`) supporting `--dry-run`, `--goal`, and `--output-dir`.
- `src/world_model.py`: Six rooms, verified Gazebo coordinates, symmetric doorway graph, and ten initial objects.
- `src/kb.py`: `KnowledgeBase` enforcing preconditions and closed-loop state updates.
- `src/pddl_generator.py`: Writes `domain/domain.pddl` and `problems/problem.pddl`.
- `src/planner.py`: Runs `fast-downward` and captures `output/plan.soln` and `output/plan.txt`.
- `src/executor.py`: Translates `move`, `pick`, and `place` actions into `ros2 run tb3_service_robot` commands (or dry-run logs).
- `src/cli.py` and `src/utils.py`: Goal validation, interactive loop, and Fast Downward plan parsing.
- `domain/domain.pddl`: Typed PDDL domain (`move`, `pick`, `place`).
- `problems/problem.pddl`: Canonical sample problem for `at cup storage`.

## Running

With `fast-downward` on your `PATH` (for example using the Docker wrapper in the [root README](../README.md)):

```bash
uv run tb3-planner --dry-run --goal "at cup storage"
```

Or interactively:

```bash
uv run tb3-planner --dry-run
```

Example goals:

- `robot-at kitchen`
- `at cup storage`
- `(holding phone)`
