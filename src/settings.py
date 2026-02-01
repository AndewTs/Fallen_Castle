import math

# ================= НАСТРОЙКИ =================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Pixel Dungeon — MVP with Treasure"

PLAYER_SPEED = 320
PLAYER_HP = 400
PLAYER_SCALE = 7

ENEMY_SCALE = 6
ENEMY_HP = 100
ENEMY_SPEED = 140

BOSS_SCALE = 0.09
BOSS_HP = 1000
BOSS_SPEED = 110

PIXEL = 6  # used for pixel-draw heart etc (optional)

SWORD_LENGTH = 100
SWORD_THICKNESS = 5
SWORD_TIME = 0.12

MAX_FLOORS = 3
BASE_FLOOR_SIZE = 3

ROOM_GRID_SIZE = 3  # size x size rooms

# door directions
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

# chance that a cleared normal room drops a key (0..1)
KEY_DROP_CHANCE = 0.25

# wall tile
WALL_TILE = 64

# projectile speed for bow
ARROW_SPEED = 700.0

HALBERD_RADIUS = 200
HALBERD_ARC_ANGLE = 65  # градусов
HALBERD_DAMAGE = 100
HALBERD_TIME = 0.22
HALBERD_COOLDOWN = 0.45

HAMMER_RADIUS = 140
HAMMER_DAMAGE = 180
HAMMER_TIME = 0.18
HAMMER_COOLDOWN = 0.75
HAMMER_WINDUP = 0.25     # задержка перед ударом
HAMMER_IMPACT = 0.15    # вспышка удара
HAMMER_SHAKE = 8        # сила тряски экрана
HAMMER_STUN_TIME = 1.2
HAMMER_BOSS_SLOW_MULT = 0.5   # 50% скорости
HAMMER_BOSS_SLOW_TIME = 2.5  # секунды



# ====================== HELPERS ======================
def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])