# dungeon.py
from room import Room
from settings import ROOM_GRID_SIZE

DIRECTIONS = {
    "up": (0, 1),
    "down": (0, -1),
    "left": (-1, 0),
    "right": (1, 0)
}

OPPOSITE = {
    "up": "down",
    "down": "up",
    "left": "right",
    "right": "left"
}


class Floor:
    def __init__(self, size=ROOM_GRID_SIZE):
        self.size = size
        self.rooms = {}  # dict[(x,y)] = Room
        self.start_pos = (0, 0)
        self.boss_pos = (size - 1, size - 1)
        self.current_pos = self.start_pos
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

        # connect doors (4-neighbors)
        for (x, y), room in list(self.rooms.items()):
            doors = {}
            for name, (dx, dy) in DIRECTIONS.items():
                npos = (x + dx, y + dy)
                if npos in self.rooms:
                    doors[name] = npos
            room.set_doors(doors)

            SCREEN_W = 1280
            SCREEN_H = 720

            DOOR_MARGIN = 200

            if "up" in doors:
                room.add_forbidden_zone(SCREEN_W // 2, SCREEN_H - 80, DOOR_MARGIN)
            if "down" in doors:
                room.add_forbidden_zone(SCREEN_W // 2, 80, DOOR_MARGIN)
            if "left" in doors:
                room.add_forbidden_zone(80, SCREEN_H // 2, DOOR_MARGIN)
            if "right" in doors:
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
