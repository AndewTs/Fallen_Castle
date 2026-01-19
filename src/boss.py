import arcade
import math
from enemy import Enemy
from projectile import Projectile


class Boss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.sprite.texture = arcade.load_texture("assets/boss.png")
        self.sprite.scale = 4
        self.max_hp = 120
        self.hp = self.max_hp
        self.phase = 1
        self.shoot_timer = 2.0
        self.dash_timer = 5.0

    def update(self, player, dt, projectiles):
        # немного более агрессивное поведение с фазами
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        # медленное приближение
        if dist > 150:
            self.sprite.center_x += (dx / dist) * (80 + 20 * self.phase) * dt
            self.sprite.center_y += (dy / dist) * (80 + 20 * self.phase) * dt


        # фазы
        if self.hp < 200:
            self.phase = 2
        if self.hp < 100:
            self.phase = 3

        # стрельба
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            self.shoot_timer = max(0.6, 2.0 - 0.4 * self.phase)
            # создаём несколько снарядов в сторону игрока (с разбросом)
            offsets = (-0.3, 0.0, 0.3) if self.phase == 1 else (-0.5, -0.2, 0.0, 0.2, 0.5)
            for off in offsets:
                projectiles.append(Projectile(self.x, self.y, player.x, player.y, angle_offset=off, speed=420 + 40*self.phase, damage=10 + 4*self.phase))

        # рывок
        self.dash_timer -= dt
        if self.dash_timer <= 0:
            self.dash_timer = max(2.0, 5.0 - self.phase)
            if dist > 10:
                nx = dx / dist
                ny = dy / dist
                dash_dist = 220 + 40 * self.phase
                self.sprite.center_x += nx * dash_dist
                self.sprite.center_y += ny * dash_dist