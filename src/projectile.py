import arcade
import math


class Projectile:
    def __init__(self, x, y, tx, ty, angle_offset=0.0, speed=400.0, damage=8):
        self.x = x
        self.y = y
        dx = tx - x
        dy = ty - y
        base = math.atan2(dy, dx)
        angle = base + angle_offset
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.damage = damage

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self):
        left = self.x - 4
        bottom = self.y - 4
        arcade.draw_lbwh_rectangle_filled(left, bottom, 8, 8, arcade.color.YELLOW)