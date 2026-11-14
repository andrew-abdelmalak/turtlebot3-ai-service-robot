# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/spec-2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-11-14

### Added

- Non-interactive `--goal` and simulation-free `--dry-run` (`--no-ros`) CLI flags via `tb3-planner` (`pyproject.toml`, `planning/src/main.py`).
- Unit and Fast Downward integration test suite (`tests/`, 19 tests) verifying Knowledge Base transitions, PDDL generation, goal validation, plan parsing, closed-loop failure aborts, stubbed ROS 2 node exit codes, and SLAM occupancy-grid coordinate alignment.
- Tracked LaTeX source under `paper/` matching Overleaf and compiled in CI with TeX Live 2025.
- Light and dark architecture and apartment topology diagrams (`docs/diagrams/`), community health files (`.github/`), `CITATION.cff`, and Dependabot configuration.

### Changed

- Updated `navigation_node.py` to compute yaw quaternions directly with `math.sin`/`math.cos`, removing the undeclared `tf_transformations` dependency.
- Resolved default PDDL and output paths relative to `planning/` rather than the caller's working directory.
- Aligned `README.md`, `planning/README.md`, and `paper/AI_Robotics_Planning.tex` with `world_model.py` and Fast Downward's 8-step, 5-room plan for `at cup storage`.
- Replaced `.github/workflows/lint.yml` with SHA-pinned CI (`ci.yml`) and paper build (`paper.yml`) workflows.

### Fixed

- Propagated non-zero exit codes from `navigation_node.py` and `gripper_node.py` when goals are canceled, rejected, or fail, enforcing closed-loop Knowledge Base preservation in `executor.py`.
- Validated goal rooms and objects in `parse_goal_input` before invoking Fast Downward, preventing translator crashes on unknown names such as `dining`.
- Fixed `parse_plan` handling of parenthesized action lines with trailing cost annotations (`(move ...) (1)`).
- Fixed ROS 2 `ament_copyright`, `ament_flake8`, and `ament_pep257` test failures in `ros/tb3_service_robot` and bumped package version to `1.1.0`.
- Eliminated PDDL translator type/predicate name-clash warnings by using `(:types room item)`.

### Removed

- Duplicate `planning/src/domain/domain.pddl` and tracked scratch artifacts under `planning/output/`.

## [1.0.0] - 2026-03-19

### Added

- Initial PDDL planning pipeline (`planning/`), ROS 2 Humble navigation and gripper client nodes (`ros/tb3_service_robot/`), custom Gazebo world and SLAM map assets (`ros/tb3_course_assets/`), and IEEE conference paper (`docs/AI_Robotics_Planning.pdf`).

[Unreleased]: https://github.com/andrew-abdelmalak/turtlebot3-ai-service-robot/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/andrew-abdelmalak/turtlebot3-ai-service-robot/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/andrew-abdelmalak/turtlebot3-ai-service-robot/releases/tag/v1.0.0
