import random
from settings import *
from room import Room


class Floor:
    def __init__(self, floor_number=1):
        self.floor_number = floor_number
        self.size = BASE_FLOOR_SIZE + (floor_number - 1)
        size = self.size
        self.rooms = {}  # dict[(x,y)] = Room
        self.start_pos = (0, 0)
        self.boss_pos = (size - 1, size - 1)
        self.current_pos = self.start_pos
        self.treasure_pos = None
        self.generate()

    def generate(self):
        # create rooms
        for x in range(self.size):
            for y in range(self.size):
                pos = (x, y)
                if pos == self.start_pos:
                    r = Room(pos, "start")
                elif pos == self.boss_pos:
                    r = Room(pos, "boss")
                else:
                    r = Room(pos, "normal")
                self.rooms[pos] = r

        # pick one random normal room to be treasure (not start, not boss)
        normal_positions = [p for p, r in self.rooms.items() if r.type == "normal"]
        if normal_positions:
            tp = random.choice(normal_positions)
            self.rooms[tp].type = "treasure"
            self.rooms[tp].treasure_unlocked = False
            self.treasure_pos = tp

        # connect doors (4-neighbors)
        for (x, y), room in list(self.rooms.items()):
            doors = {}
            for name, (dx, dy) in DIRECTIONS.items():
                npos = (x + dx, y + dy)
                if npos in self.rooms:
                    doors[name] = npos
            room.set_doors(doors)

        # Add forbidden zones for doors & start
        SCREEN_W = SCREEN_WIDTH
        SCREEN_H = SCREEN_HEIGHT
        DOOR_MARGIN = 140
        for (x, y), room in self.rooms.items():
            if "up" in room.doors:
                room.add_forbidden_zone(SCREEN_W // 2, SCREEN_H - 80, DOOR_MARGIN)
            if "down" in room.doors:
                room.add_forbidden_zone(SCREEN_W // 2, 80, DOOR_MARGIN)
            if "left" in room.doors:
                room.add_forbidden_zone(80, SCREEN_H // 2, DOOR_MARGIN)
            if "right" in room.doors:
                room.add_forbidden_zone(SCREEN_W - 80, SCREEN_H // 2, DOOR_MARGIN)
            if room.type == "start":
                room.add_forbidden_zone(SCREEN_W // 2, 190, 200)

    def get_current_room(self):
        return self.rooms[self.current_pos]

    def move(self, pos):
        if pos in self.rooms:
            self.current_pos = pos
            return True
        return False