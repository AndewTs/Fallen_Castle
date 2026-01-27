# room.py
import random

class Room:
    def __init__(self, pos, room_type="normal"):
        """
        pos: (x, y) tuple
        room_type: "start", "normal", "boss"
        """
        self.pos = pos
        self.type = room_type
        self.doors = {}  # filled by Floor: {"up": (x,y), ...}
        self.enemy_spawns = []  # list of dicts {"type":"enemy"/"boss","x":int,"y":int,"hp":int}
        self.walls = []  # optional positions of obstacles
        self.forbidden_zones = []

        # enemy count by type
        if self.type == "start":
            cnt = 0
        elif self.type == "boss":
            cnt = 0
        else:
            cnt = random.randint(2, 4)

        # generate spawns (positions will be used when loading)
        for _ in range(cnt):
            ex = random.randint(200, 1080)
            ey = random.randint(220, 620)
            self.enemy_spawns.append({"type": "enemy", "x": ex, "y": ey, "hp": None})

    def set_doors(self, doors_dict):
        self.doors = doors_dict

    def add_forbidden_zone(self, x, y, radius):
        self.forbidden_zones.append((x, y, radius))
