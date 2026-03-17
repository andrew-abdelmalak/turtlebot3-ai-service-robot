class KnowledgeBase:
    def __init__(self, world):
        self.rooms = world.rooms
        self.objects = dict(world.objects)
        self.robot_room = "livingroom"
        self.holding = None
        self.connected = world.connected
    
    def get_init_facts(self):
        facts = []

        for r in self.rooms:
            facts.append(f"(room {r})")

        facts.append(f"(robot-at {self.robot_room})")

        for o, r in self.objects.items():
            facts.append(f"(object {o})")
            facts.append(f"(at {o} {r})")

        for (a, b) in self.connected:
            facts.append(f"(connected {a} {b})")

        if self.holding:
            # Still declare the held item as an object so place remains applicable.
            facts.append(f"(object {self.holding})")
            facts.append(f"(holding {self.holding})")
        else:
            facts.append("(handempty)")

        return facts

    # Updates after executing plan actions
    def apply_move(self, to_room):
        self.robot_room = to_room

    def apply_pick(self, obj):
        if self.holding:
            raise ValueError(f"Cannot pick {obj} while already holding {self.holding}")
        if obj not in self.objects:
            raise ValueError(f"Object {obj} not found to pick")
        self.holding = obj
        del self.objects[obj]

    def apply_place(self, obj):
        if self.holding != obj:
            raise ValueError(f"Cannot place {obj} when holding {self.holding}")
        self.objects[obj] = self.robot_room
        self.holding = None
