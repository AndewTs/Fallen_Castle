import math
import arcade
import json
from enum import Enum


with open("config/config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)


SCREEN_WIDTH = CONFIG["screen"]["SCREEN_WIDTH"]
SCREEN_HEIGHT = CONFIG["screen"]["SCREEN_HEIGHT"]
SCREEN_TITLE = CONFIG["screen"]["SCREEN_TITLE"]

PLAYER_SPEED = CONFIG["player"]["PLAYER_SPEED"]
PLAYER_HP = CONFIG["player"]["PLAYER_HP"]
PLAYER_SCALE = CONFIG["player"]["PLAYER_SCALE"]

ENEMY_SCALE = CONFIG["enemy"]["ENEMY_SCALE"]
ENEMY_HP = CONFIG["enemy"]["ENEMY_HP"]
ENEMY_SPEED = CONFIG["enemy"]["ENEMY_SPEED"]

BOSS_SCALE = CONFIG["boss"]["BOSS_SCALE"]
BOSS_HP = CONFIG["boss"]["BOSS_HP"]
BOSS_SPEED = CONFIG["boss"]["BOSS_SPEED"]

PIXEL = CONFIG["pixel"]

MAX_FLOORS = CONFIG["floor"]["MAX_FLOORS"]
BASE_FLOOR_SIZE = CONFIG["floor"]["BASE_FLOOR_SIZE"]

ROOM_GRID_SIZE = CONFIG["floor"]["ROOM_GRID_SIZE"]

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

KEY_DROP_CHANCE = CONFIG["floor"]["KEY_DROP_CHANCE"]
WALL_TILE = CONFIG["floor"]["WALL_TILE"]

ARROW_SPEED = CONFIG["weapons"]["ARROW_SPEED"]

SWORD_LENGTH = CONFIG["weapons"]["SWORD_LENGTH"]
SWORD_THICKNESS = CONFIG["weapons"]["SWORD_THICKNESS"]
SWORD_TIME = CONFIG["weapons"]["SWORD_TIME"]

HALBERD_RADIUS = CONFIG["weapons"]["HALBERD_RADIUS"]
HALBERD_ARC_ANGLE = CONFIG["weapons"]["HALBERD_ARC_ANGLE"]
HALBERD_DAMAGE = CONFIG["weapons"]["HALBERD_DAMAGE"]
HALBERD_TIME = CONFIG["weapons"]["HALBERD_TIME"]
HALBERD_COOLDOWN = CONFIG["weapons"]["HALBERD_COOLDOWN"]

HAMMER_RADIUS = CONFIG["weapons"]["HAMMER_RADIUS"]
HAMMER_DAMAGE = CONFIG["weapons"]["HAMMER_DAMAGE"]
HAMMER_TIME = CONFIG["weapons"]["HAMMER_TIME"]
HAMMER_COOLDOWN = CONFIG["weapons"]["HAMMER_COOLDOWN"]
HAMMER_WINDUP = CONFIG["weapons"]["HAMMER_WINDUP"]
HAMMER_IMPACT = CONFIG["weapons"]["HAMMER_IMPACT"]
HAMMER_SHAKE = CONFIG["weapons"]["HAMMER_SHAKE"]
HAMMER_STUN_TIME = CONFIG["weapons"]["HAMMER_STUN_TIME"]
HAMMER_BOSS_SLOW_MULT = CONFIG["weapons"]["HAMMER_BOSS_SLOW_MULT"]
HAMMER_BOSS_SLOW_TIME = CONFIG["weapons"]["HAMMER_BOSS_SLOW_TIME"]

BUTTON_NORMAL = (87, 76, 41)
BUTTON_HOVER = (128, 112, 61)
BUTTON_PRESSED = (107, 92, 44)
TEXT_COLOR = (255, 255, 255, 255)
BUTTON_BORDER = (130, 114, 62)
UI_BACKGROUND = (40, 40, 40, 200)

# Добавляем глобальную переменную для отслеживания пройденных уровней
completed_levels = {1: False, 2: False, 3: False}

class RoomType(Enum):
    START = "start"
    NORMAL = "normal"
    BOSS = "boss"
    TREASURE = "treasure"
    WEAPON = "weapon"  # Добавляем тип комнаты для оружия
    SHIELD = "shield"  # Добавляем тип комнаты для щита


HEART_MATRIX = [
    "0100010",
    "1110111",
    "1111111",
    "0111110",
    "0011100",
    "0001000",
]

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def draw_pixel_matrix(matrix, x, y, color):
    for r, row in enumerate(matrix):
        for c, cell in enumerate(row):
            if cell == "1":
                left = x + c * PIXEL
                bottom = y - (r + 1) * PIXEL
                arcade.draw_lbwh_rectangle_filled(left, bottom, PIXEL, PIXEL, color)