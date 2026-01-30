# player.py
import arcade
from settings import PLAYER_HP, PLAYER_SCALE, PLAYER_SPEED


class Player:
    def __init__(self, x, y):
        # try to load sprite, fallback to solid color
        try:
            self.sprite = arcade.Sprite("assets/player.png", scale=PLAYER_SCALE)
        except Exception:
            self.sprite = arcade.SpriteSolidColor(32, 48, arcade.color.BLUE)
        self.sprite.center_x = x
        self.sprite.center_y = y

        self.speed = PLAYER_SPEED
        self.hp = PLAYER_HP
        self.max_hp = PLAYER_HP

        # weapon: "sword" (default), "axe", "bow"
        self.weapon = "bow"

        # keys count
        self.keys = 0

        # attack timer
        self.attack_cooldown = 0.25
        self.attack_timer = 0.0

    @property
    def x(self):
        return self.sprite.center_x

    @property
    def y(self):
        return self.sprite.center_y

    def update(self, dt, keys_held):
        # reduce attack timer
        if self.attack_timer > 0:
            self.attack_timer -= dt

    def can_attack(self):
        return self.attack_timer <= 0

    def reset_attack(self):
        self.attack_timer = self.attack_cooldown

