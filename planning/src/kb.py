"""In-memory Knowledge Base tracking robot location, held item, and object rooms."""

from __future__ import annotations

from typing import Protocol


class WorldLike(Protocol):
    """Protocol describing the world model attributes used by KnowledgeBase."""

    rooms: list[str]
    objects: dict[str, str]
    connected: list[tuple[str, str]]


class KnowledgeBase:
    """Symbolic state of the apartment updated only after confirmed action execution."""

    def __init__(self, world: WorldLike, initial_room: str = "livingroom") -> None:
        if initial_room not in world.rooms:
            raise ValueError(f"Unknown initial room '{initial_room}'")
        self.rooms: list[str] = list(world.rooms)
        self.objects: dict[str, str] = dict(world.objects)
        self.robot_room: str = initial_room
        self.holding: str | None = None
        self.connected: list[tuple[str, str]] = list(world.connected)

    @property
    def known_objects(self) -> set[str]:
        """Return all object names currently tracked (placed or held)."""
        names = set(self.objects.keys())
        if self.holding is not None:
            names.add(self.holding)
        return names

    def get_init_facts(self) -> list[str]:
        """Return PDDL :init predicate facts reflecting the current symbolic state."""
        facts: list[str] = [f"(robot-at {self.robot_room})"]

        for obj, room in self.objects.items():
            facts.append(f"(at {obj} {room})")

        for room_a, room_b in self.connected:
            facts.append(f"(connected {room_a} {room_b})")

        if self.holding is not None:
            facts.append(f"(holding {self.holding})")
        else:
            facts.append("(handempty)")

        return facts

    def apply_move(self, to_room: str) -> None:
        """Update robot location after a confirmed move action."""
        if to_room not in self.rooms:
            raise ValueError(f"Cannot move to unknown room '{to_room}'")
        if (self.robot_room, to_room) not in self.connected:
            raise ValueError(f"Room '{to_room}' is not connected to '{self.robot_room}'")
        self.robot_room = to_room

    def apply_pick(self, obj: str) -> None:
        """Update state after a confirmed pick action."""
        if self.holding is not None:
            raise ValueError(f"Cannot pick '{obj}' while already holding '{self.holding}'")
        if obj not in self.objects:
            raise ValueError(f"Object '{obj}' not found to pick")
        if self.objects[obj] != self.robot_room:
            raise ValueError(f"Object '{obj}' is in '{self.objects[obj]}', not '{self.robot_room}'")
        self.holding = obj
        del self.objects[obj]

    def apply_place(self, obj: str) -> None:
        """Update state after a confirmed place action."""
        if self.holding != obj:
            raise ValueError(f"Cannot place '{obj}' when holding '{self.holding}'")
        self.objects[obj] = self.robot_room
        self.holding = None
