import random
from src.settings import *
from src.room import Room


class Floor:
    def __init__(self, floor_number=1):
        self.floor_number = floor_number
        self.size = BASE_FLOOR_SIZE + (floor_number - 1)
        self.rooms = {}
        self.start_pos = (0, 0)
        self.boss_pos = (self.size - 1, self.size - 1)
        self.current_pos = self.start_pos
        self.treasure_pos = None
        self.weapon_rooms = []  # Комнаты с оружием
        self.shield_room = None  # Комната со щитом (для 2 и 3 уровней)
        self.generate()

    def generate(self):
        for x in range(self.size):
            for y in range(self.size):
                pos = (x, y)
                if pos == self.start_pos:
                    r = Room(pos, RoomType.START)
                elif pos == self.boss_pos:
                    r = Room(pos, RoomType.BOSS)
                else:
                    r = Room(pos, RoomType.NORMAL)
                self.rooms[pos] = r

        normal_positions = [p for p, r in self.rooms.items() if r.type == RoomType.NORMAL]
        
        if normal_positions:
            # Выбираем комнату для сокровищницы
            tp = random.choice(normal_positions)
            self.rooms[tp].type = RoomType.TREASURE
            self.rooms[tp].treasure_unlocked = False
            self.treasure_pos = tp
            normal_positions.remove(tp)

        for (x, y), room in list(self.rooms.items()):
            doors = {}
            for name, (dx, dy) in DIRECTIONS.items():
                npos = (x + dx, y + dy)
                if npos in self.rooms:
                    doors[name] = npos
            room.set_doors(doors)

        DOOR_MARGIN = 140
        for (x, y), room in self.rooms.items():
            if "up" in room.doors:
                room.add_forbidden_zone(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80, DOOR_MARGIN)
            if "down" in room.doors:
                room.add_forbidden_zone(SCREEN_WIDTH // 2, 80, DOOR_MARGIN)
            if "left" in room.doors:
                room.add_forbidden_zone(80, SCREEN_HEIGHT // 2, DOOR_MARGIN)
            if "right" in room.doors:
                room.add_forbidden_zone(SCREEN_WIDTH - 80, SCREEN_HEIGHT // 2, DOOR_MARGIN)
            if room.type == RoomType.START:
                room.add_forbidden_zone(SCREEN_WIDTH // 2, 190, 200)

    def get_current_room(self):
        return self.rooms[self.current_pos]

    def move(self, pos):
        if pos in self.rooms:
            self.current_pos = pos
            return True
        return False