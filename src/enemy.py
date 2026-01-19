import arcade
import math

class Enemy:
    def __init__(self, x, y):
        self.sprite = arcade.Sprite(
            "assets/enemy.png",
            scale=0.09
        )
        self.sprite.center_x = x
        self.sprite.center_y = y

        self.hp = 60
        self.speed = 200

    @property
    def x(self):
        return self.sprite.center_x

    @property
    def y(self):
        return self.sprite.center_y

    def update(self, player, dt):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        # простой AI
        if dist < 350 and dist > 1:
            self.sprite.center_x += dx / dist * self.speed * dt
            self.sprite.center_y += dy / dist * self.speed * dt

            if dx > 0:
                self.sprite.scale_x = -abs(self.sprite.scale_x)
            else:
                self.sprite.scale_x = +abs(self.sprite.scale_x)