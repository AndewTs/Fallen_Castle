# settings.py
import math

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Fallen Castle"

PLAYER_SPEED = 320
PLAYER_HP = 100
PLAYER_SCALE = 7

ENEMY_SCALE = 6
ENEMY_HP = 40
ENEMY_SPEED = 140

BOSS_SCALE = 0.09
BOSS_HP = 1000
BOSS_SPEED = 110

SWORD_LENGTH = 64
SWORD_THICKNESS = 3
SWORD_TIME = 0.12

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

# chance of a key
KEY_DROP_CHANCE = 0.25

# wall tile
WALL_TILE = 64

# projectile speed for bow
ARROW_SPEED = 700.0

# help func for boss and enemy ai
def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

