from world_model import connected, objects, rooms
from kb import KnowledgeBase
from cli import run_cli


class World:
    def __init__(self):
        self.rooms = rooms
        self.objects = objects
        self.connected = connected

world = World()
kb = KnowledgeBase(world)
run_cli(kb, world)

