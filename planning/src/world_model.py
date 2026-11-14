"""Apartment world model: rooms, Gazebo coordinates, doorway graph, and initial objects."""

rooms: list[str] = [
    "kitchen",
    "diningroom",
    "livingroom",
    "bedroom",
    "storage",
    "bathroom",
]

coordinates: dict[str, tuple[float, float]] = {
    "storage": (-4.5, -1.5),
    "livingroom": (-1.0, 1.5),
    "diningroom": (6.0, 1.0),
    "bathroom": (3.0, 5.0),
    "bedroom": (-4.5, 3.5),
    "kitchen": (8.5, -1.5),
}

connected: list[tuple[str, str]] = [
    ("storage", "bedroom"),
    ("bedroom", "storage"),
    ("livingroom", "bedroom"),
    ("bedroom", "livingroom"),
    ("livingroom", "diningroom"),
    ("diningroom", "livingroom"),
    ("bathroom", "diningroom"),
    ("diningroom", "bathroom"),
    ("diningroom", "kitchen"),
    ("kitchen", "diningroom"),
]

objects: dict[str, str] = {
    "cup": "kitchen",
    "pan": "kitchen",
    "plate": "diningroom",
    "notebook": "diningroom",
    "bottle": "livingroom",
    "remote": "livingroom",
    "book": "bedroom",
    "phone": "bedroom",
    "keys": "storage",
    "towel": "bathroom",
}
