"""Tests verifying the apartment world model against the SLAM map and Gazebo assets."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from planning.src import world_model

REPO_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = REPO_ROOT / "ros" / "tb3_course_assets"


def _read_pgm_binary(path: Path) -> tuple[int, int, int, bytes]:
    """Parse a binary P5 PGM occupancy grid file."""
    data = path.read_bytes()
    if not data.startswith(b"P5"):
        raise AssertionError(f"Expected binary PGM (P5), got {data[:10]!r}")

    idx = 2
    tokens: list[bytes] = []
    while len(tokens) < 3:
        while idx < len(data) and data[idx : idx + 1] in (b" ", b"\t", b"\r", b"\n"):
            idx += 1
        if data[idx : idx + 1] == b"#":
            while idx < len(data) and data[idx : idx + 1] != b"\n":
                idx += 1
            continue
        start = idx
        while idx < len(data) and data[idx : idx + 1] not in (b" ", b"\t", b"\r", b"\n", b"#"):
            idx += 1
        tokens.append(data[start:idx])

    # Single whitespace byte separates maxval from raw pixel bytes.
    idx += 1
    width, height, maxval = (int(t) for t in tokens)
    pixels = data[idx:]
    assert len(pixels) == width * height, f"Expected {width * height} pixels, got {len(pixels)}"
    return width, height, maxval, pixels


def _parse_map_yaml(path: Path) -> tuple[float, float, float]:
    """Extract resolution and origin (x, y) from map.yaml without PyYAML."""
    resolution = None
    origin_x = None
    origin_y = None
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("resolution:"):
            resolution = float(stripped.split(":", 1)[1].strip())
        elif stripped.startswith("origin:"):
            raw = stripped.split(":", 1)[1].strip().strip("[]")
            parts = [float(p.strip()) for p in raw.split(",")]
            origin_x, origin_y = parts[0], parts[1]
    assert resolution is not None and origin_x is not None and origin_y is not None
    return resolution, origin_x, origin_y


def test_world_model_graph_and_objects() -> None:
    """Verify rooms, coordinates, symmetric edges, and initial object placements."""
    assert len(world_model.rooms) == 6
    assert len(world_model.objects) == 10
    assert set(world_model.coordinates.keys()) == set(world_model.rooms)

    edges = set(world_model.connected)
    for room_a, room_b in edges:
        assert room_a in world_model.rooms
        assert room_b in world_model.rooms
        assert (room_b, room_a) in edges, f"Edge ({room_a}, {room_b}) must be bidirectional"

    for obj, room in world_model.objects.items():
        assert obj
        assert room in world_model.rooms


def test_room_coordinates_land_on_free_space_in_slam_map() -> None:
    """Verify all six room coordinates fall inside free space (pixel 254) on map.pgm."""
    resolution, origin_x, origin_y = _parse_map_yaml(ASSETS_DIR / "maps" / "map.yaml")
    width, height, maxval, pixels = _read_pgm_binary(ASSETS_DIR / "maps" / "map.pgm")
    assert maxval == 255

    for room, (wx, wy) in world_model.coordinates.items():
        col = int(round((wx - origin_x) / resolution))
        row_from_bottom = int(round((wy - origin_y) / resolution))
        row_from_top = height - 1 - row_from_bottom
        assert 0 <= col < width, f"{room} x-coordinate out of map bounds"
        assert 0 <= row_from_top < height, f"{room} y-coordinate out of map bounds"
        pixel = pixels[row_from_top * width + col]
        assert pixel == 254, f"Room {room} at ({wx}, {wy}) landed on pixel {pixel}, expected free (254)"


def test_ros_and_gazebo_xml_assets_parse_cleanly() -> None:
    """Ensure all XML/SDF assets in ros/ are well-formed XML."""
    xml_files = [
        REPO_ROOT / "ros" / "tb3_service_robot" / "package.xml",
        ASSETS_DIR / "models" / "tb3_house_custom" / "model.config",
        ASSETS_DIR / "models" / "tb3_house_custom" / "model.sdf",
        ASSETS_DIR / "worlds" / "my_house.world",
    ]
    for path in xml_files:
        assert path.exists(), f"Missing asset file: {path}"
        ET.parse(path)
