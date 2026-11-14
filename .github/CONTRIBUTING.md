# Contributing

We welcome bug reports, documentation fixes, and targeted improvements to the PDDL planning and ROS 2 bridge layers.

## Setup and checks

CI runs the following checks on every pull request targeting `main`:

```bash
uv sync --locked --all-groups
uv run ruff check .
uv run ruff format --check .
uv run pytest -v
uv run tb3-planner --dry-run --goal "at cup storage"
```

To run the Fast Downward integration tests in `tests/test_planner_integration.py`, ensure `fast-downward` is on your `PATH` (see the root [README](../README.md#quick-start-dry-run-without-gazebo) for the pinned Docker wrapper).

### ROS 2 package checks

```bash
docker run --rm --network=none \
  -u "$(id -u):$(id -g)" \
  -v "$PWD/ros/tb3_service_robot:/ws/src/tb3_service_robot:ro" \
  -w /ws \
  ros:humble-ros-base@sha256:d9f14e84747bea639a65e00cf871d2c68ae55385d2acf6239614de0cadb41dcc \
  bash -c "source /opt/ros/humble/setup.bash && \
    colcon --log-base /tmp/log build --build-base /tmp/build --install-base /tmp/install && \
    colcon --log-base /tmp/log test --build-base /tmp/build --install-base /tmp/install && \
    colcon --log-base /tmp/log test-result --test-result-base /tmp/build --verbose"
```

### Paper build

```bash
docker run --rm --network=none \
  -u "$(id -u):$(id -g)" \
  -v "$PWD/paper:/work" \
  -w /work \
  texlive/texlive:TL2025-historic@sha256:7056390eac37715fd3e01875037ceb4016cb17d44c611f7bbbfa7a012007979f \
  latexmk -pdf -no-shell-escape -interaction=nonstopmode -halt-on-error AI_Robotics_Planning.tex
```

## Pull requests and commits

- Target the `main` branch.
- Write clear, imperative commit subjects (for example, `fix(planning): validate goal rooms before search`).
- Keep changes scoped and include tests for behavior fixes.
- Contributions are licensed under the project [MIT License](../LICENSE).
