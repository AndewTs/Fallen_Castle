# enemy.py
import arcade
import math
import random
from settings import ENEMY_SCALE, ENEMY_HP, ENEMY_SPEED, ARROW_SPEED
class Enemy:
    def __init__(self, x, y, hp=None, speed=None):
        # try asset
        try:
            self.sprite = arcade.Sprite("assets/enemy 2.png", scale=ENEMY_SCALE)
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


class FastEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=25, speed=260)
        self.sprite.texture = arcade.load_texture("assets/enemy_fast.png")


class TankEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=140, speed=70)
        self.sprite.texture = arcade.load_texture("assets/enemy_tank.png")


class RangedEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=40, speed=80)
        self.sprite.texture = arcade.load_texture("assets/enemy_ranged.png")
        self.shoot_cd = 1.5
        self.timer = 0
        self.timer = random.uniform(0.3, 1.2)
    
    def try_shoot(self, player, projectile_list):
        if self.timer > 0:
            return

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist < 160 or dist > 520:
            return

        dx /= dist
        dy /= dist

        arrow = arcade.Sprite("assets/arrow.png", scale=5)
        arrow.center_x = self.x + dx * 36
        arrow.center_y = self.y + dy * 36

        arrow.change_x = dx * ARROW_SPEED
        arrow.change_y = dy * ARROW_SPEED
        arrow.angle = math.degrees(math.atan2(dx, dy))

        arrow.damage = 15
        arrow.from_enemy = True
        arrow.time_alive = 0

        projectile_list.append(arrow)
        self.timer = self.shoot_cd

    def update(self, player, walls, dt, projectile_list):
        self.timer -= dt
        self.try_shoot(player, projectile_list)

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        # держит дистанцию
        if dist < 220:
            vx = -dx / dist * self.speed * dt
            vy = -dy / dist * self.speed * dt
        elif dist > 360:
            vx = dx / dist * self.speed * dt
            vy = dy / dist * self.speed * dt
        else:
            vx = vy = 0

        ox = self.sprite.center_x
        self.sprite.center_x += vx
        if arcade.check_for_collision_with_list(self.sprite, walls):
            self.sprite.center_x = ox

        oy = self.sprite.center_y
        self.sprite.center_y += vy
        if arcade.check_for_collision_with_list(self.sprite, walls):
            self.sprite.center_y = oy, ENEMY_HP, ENEMY_SPEED

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

