# enemy.py
import arcade
import math
import random
from settings import ENEMY_SCALE, ENEMY_HP, ENEMY_SPEED

class Enemy:
    def __init__(self, x, y, hp=None, speed=None):
        # try asset
        try:
            self.sprite = arcade.Sprite("assets/enemy.png", scale=ENEMY_SCALE)
        except Exception:
            self.sprite = arcade.SpriteSolidColor(28, 28, arcade.color.RED)
        self.sprite.center_x = x
        self.sprite.center_y = y

        self.hp = hp if hp is not None else ENEMY_HP
        self.speed = speed if speed is not None else ENEMY_SPEED

    @property
    def x(self):
        return self.sprite.center_x

    @property
    def y(self):
        return self.sprite.center_y

    @property
    def alive(self):
        return self.hp > 0

    def update(self, player, walls, dt):
        # simple seek AI
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist < 360 and dist > 1:
            vx = dx / dist * self.speed * dt
            vy = dy / dist * self.speed * dt

            # move x and check collision
            old_x = self.sprite.center_x
            self.sprite.center_x += vx
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_x = old_x

            # move y and check collision
            old_y = self.sprite.center_y
            self.sprite.center_y += vy
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_y = old_y

            # flip sprite
            if dx > 0:
                self.sprite.scale_x = abs(self.sprite.scale_x)
            else:
                self.sprite.scale_x = -abs(self.sprite.scale_x)

    @staticmethod
    def random_spawn(margin_x=200, margin_y=150):
        x = random.randint(margin_x, 1280 - margin_x)
        y = random.randint(margin_y, 720 - margin_y)
        return Enemy(x, y)
