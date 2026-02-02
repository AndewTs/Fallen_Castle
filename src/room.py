import random
from src.settings import SCREEN_HEIGHT, SCREEN_WIDTH, RoomType


class Room:
    def __init__(self, pos, room_type="normal"):
        self.pos = pos
        self.type = room_type
        self.doors = {}
        self.enemy_spawns = []
        self.walls = []
        self.forbidden_zones = []
        self.treasure_unlocked = False
        self.guaranteed_item = None  # Добавляем гарантированный предмет
        self.item_spawned = False  # Флаг, что предмет уже размещен

        if self.type == RoomType.START:
            cnt = 0
        elif self.type == RoomType.BOSS:
            cnt = 0
        elif self.type == RoomType.TREASURE:
            cnt = 0
        else:
            cnt = random.randint(2, 4)

        for _ in range(cnt):
            ex = random.randint(200, SCREEN_WIDTH - 200)
            ey = random.randint(220, SCREEN_HEIGHT - 100)
            self.enemy_spawns.append({"type": "enemy", "x": ex, "y": ey, "hp": None})

    def set_doors(self, doors_dict):
        self.doors = doors_dict

    def add_forbidden_zone(self, x, y, radius):
        self.forbidden_zones.append((x, y, radius))