import json
from pathlib import Path

CONFIG_PATH = Path("config/settings.json")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

# Окно
SCREEN_WIDTH = CONFIG["window"]["width"]
SCREEN_HEIGHT = CONFIG["window"]["height"]
SCREEN_TITLE = CONFIG["window"]["title"]

# Игрок
PLAYER_SPEED = CONFIG["player"]["speed"]
PLAYER_MAX_HP = CONFIG["player"]["max_hp"]
ATTACK_COOLDOWN = CONFIG["player"]["attack_cooldown"]
PLAYER_SPRITE = CONFIG["player"]["sprite"]
PLAYER_SCALE = CONFIG["player"]["scale"]

# Враги
ENEMY_SPEED = CONFIG["enemy"]["speed"]
ENEMY_HP = CONFIG["enemy"]["hp"]
ENEMY_SPRITE = CONFIG["enemy"]["sprite"]
ENEMY_SCALE = CONFIG["enemy"]["scale"]

# Босс
BOSS_SPEED = CONFIG["boss"]["speed"]
BOSS_MAX_HP = CONFIG["boss"]["max_hp"]
BOSS_SPRITE = CONFIG["boss"]["sprite"]
BOSS_SCALE = CONFIG["boss"]["scale"]
