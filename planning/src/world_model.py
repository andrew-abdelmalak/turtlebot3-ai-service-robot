rooms = ["kitchen", "diningroom", "livingroom", "bedroom", "storage", "bathroom"]

coordinates = {
    "storage": (-4.5, -1.5),    # bottom-left 
    "livingroom": (-1.0, 1.5),  # top-middle
    "diningroom": (6.0, 1.0),   # top-right
    "bathroom": (3.0, 5.0),     # central small enclosed room
    "bedroom": (-4.5, 3.5),     # top-left 
    "kitchen": (8.5, -1.5)      # bottom-right
}

connected = [
    ("storage", "bedroom"),
    ("bedroom", "storage"),
    ("livingroom", "bedroom"),
    ("bedroom", "livingroom"),
    ("livingroom", "diningroom"),
    ("diningroom", "livingroom"),
    ("bathroom", "diningroom"),
    ("diningroom", "bathroom"),
    ("diningroom", "kitchen"),
    ("kitchen", "diningroom")
]

objects = {
    "cup": "kitchen",
    "pan": "kitchen",
    "plate": "diningroom",
    "notebook": "diningroom",
    "bottle": "livingroom",
    "remote": "livingroom",
    "book": "bedroom",
    "phone": "bedroom",
    "keys": "storage",
    "towel": "bathroom"
}
