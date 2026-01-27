# boss.py
import arcade
import math
from enemy import Enemy
from settings import BOSS_SCALE, BOSS_HP, BOSS_SPEED

class Boss(Enemy):
    def __init__(self, x, y):
        # reuse enemy constructor but with boss sprite if exists
        try:
            self.sprite = arcade.Sprite("assets/boss.png", scale=BOSS_SCALE)
        except Exception:
            self.sprite = arcade.SpriteSolidColor(64, 64, arcade.color.PURPLE)
        self.sprite.center_x = x
        self.sprite.center_y = y

        self.hp = BOSS_HP
        self.max_hp = BOSS_HP
        self.speed = BOSS_SPEED

        self.phase = 1

    @property
    def alive(self):
        return self.hp > 0

    def update_phase(self, player, walls, dt):
        hp_ratio = self.hp / self.max_hp

        if hp_ratio <= 0.33:
            self.phase = 3
        elif hp_ratio <= 0.66:
            self.phase = 2
        else:
            self.phase = 1

        # boss simple behavior: slow approach + occasional dash (simplified)
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 120:
            speed_multiplier = {
                    1: 0.6,
                    2: 1.3,
                            }[self.phase]

            vx = dx / dist * (self.speed * speed_multiplier) * dt
            vy = dy / dist * (self.speed * speed_multiplier) * dt

            old_x = self.sprite.center_x
            self.sprite.center_x += vx
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_x = old_x
            old_y = self.sprite.center_y
            self.sprite.center_y += vy
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_y = old_y

        # flip sprite
        if dx > 0:
            self.sprite.scale_x = abs(self.sprite.scale_x)
        else:
            self.sprite.scale_x = -abs(self.sprite.scale_x)
