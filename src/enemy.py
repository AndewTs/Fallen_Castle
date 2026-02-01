# enemy.py
import arcade
import math
import random
from settings import ENEMY_SCALE, ENEMY_HP, ENEMY_SPEED, ARROW_SPEED


class Enemy:
    def __init__(self, x, y, hp=None, speed=None):
        # try asset
        self.stunned = False
        self.stun_timer = 0.0
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
        if self.stunned:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.stunned = False
            return
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

        arrow.damage = 1
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
            self.sprite.center_y = oy


class EliteRunner(FastEnemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.dash_cd = random.uniform(1.5, 2.5)
        self.dash_timer = 0.0
        self.is_dashing = False
        self.dash_dir = (0, 0)
        self.dash_speed = 900

        self.hp = 45  # чуть жирнее обычного бегуна

    def update(self, player, walls, dt):
        if self.stunned:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.stunned = False
            return
        self.dash_cd -= dt

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        # старт рывка
        if not self.is_dashing and self.dash_cd <= 0 and dist > 60:
            self.is_dashing = True
            self.dash_timer = 0.25
            self.dash_cd = random.uniform(2.0, 3.0)
            self.dash_dir = (dx / max(dist, 1), dy / max(dist, 1))

        if self.is_dashing:
            self.dash_timer -= dt
            vx = self.dash_dir[0] * self.dash_speed * dt
            vy = self.dash_dir[1] * self.dash_speed * dt

            ox = self.sprite.center_x
            oy = self.sprite.center_y

            self.sprite.center_x += vx
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_x = ox
                self.is_dashing = False

            self.sprite.center_y += vy
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_y = oy
                self.is_dashing = False

            if self.dash_timer <= 0:
                self.is_dashing = False
        else:
            # обычное поведение бегуна
            super().update(player, walls, dt)
        
        self.sprite.color = arcade.color.PURPLE_HEART


class EliteShooter(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=55, speed=90)
        self.shoot_cd = random.uniform(3.0, 4.0)
        self.timer = random.uniform(1.5, 3)

    def update(self, player, walls, dt, projectile_list):
        if self.stunned:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.stunned = False
            return
        self.timer -= dt

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        # движение — просто идёт на игрока
        if dist > 1:
            vx = dx / dist * self.speed * dt
            vy = dy / dist * self.speed * dt

            ox = self.sprite.center_x
            self.sprite.center_x += vx
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_x = ox

            oy = self.sprite.center_y
            self.sprite.center_y += vy
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_y = oy

        # стрельба
        if self.timer <= 0 and dist < 520:
            dx /= max(dist, 1)
            dy /= max(dist, 1)

            arrow = arcade.Sprite("assets/arrow.png", scale=4)
            arrow.center_x = self.x
            arrow.center_y = self.y
            arrow.change_x = dx * 200   # медленная стрела
            arrow.change_y = dy * 200
            arrow.damage = 12
            arrow.from_enemy = True

            projectile_list.append(arrow)
            self.timer = self.shoot_cd
        
        self.sprite.color = arcade.color.PURPLE_HEART


class EliteTankFloor3(TankEnemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = 260
        self.speed = 55

        self.slam_cd = random.uniform(2.5, 4.0)
        self.slam_timer = 0.0
        self.slam_radius = 140
        self.slam_damage = 35
        self.slow_duration = 2.5

        self.is_slamming = False
        self.warn_time = 0.6  # визуальное предупреждение
        self.warn_timer = 0.0

        self.sprite.color = arcade.color.DARK_RED

    def update(self, player, walls, dt):
        if self.stunned:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.stunned = False
            return
        self.slam_timer -= dt

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        # ───── START SLAM ─────
        if not self.is_slamming and self.slam_timer <= 0 and dist < 220:
            self.is_slamming = True
            self.warn_timer = self.warn_time
            self.slam_timer = random.uniform(3.0, 4.5)

        # ───── SLAM WARNING ─────
        if self.is_slamming:
            self.warn_timer -= dt

            if self.warn_timer <= 0:
                # APPLY SLAM
                if dist <= self.slam_radius:
                    player.hp -= self.slam_damage
                    player.slow_timer = max(player.slow_timer, self.slow_duration)

                self.is_slamming = False
            return  # во время удара не двигается

        # ───── NORMAL MOVE ─────
        if dist > 60:
            vx = dx / dist * self.speed * dt
            vy = dy / dist * self.speed * dt

            ox = self.sprite.center_x
            self.sprite.center_x += vx
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_x = ox

            oy = self.sprite.center_y
            self.sprite.center_y += vy
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_y = oy

        # flip
        if dx > 0:
            self.sprite.scale_x = abs(self.sprite.scale_x)
        else:
            self.sprite.scale_x = -abs(self.sprite.scale_x)

        self.sprite.color = arcade.color.PURPLE_HEART


class EliteArcherFloor3(RangedEnemy):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.volley_cooldown = random.uniform(3.0, 4.5)
        self.volley_timer = self.volley_cooldown

        self.in_volley = False
        self.volley_count = 0
        self.max_volley = random.randint(3, 5)
        self.volley_interval = 0.3
        self.volley_interval_timer = 0.0

        self.sprite.color = arcade.color.PURPLE_HEART

    def update(self, player, walls, dt, projectile_list):
        if self.stunned:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.stunned = False
            return
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        # ───── движение (просто идёт на игрока) ─────
        if not self.in_volley and dist > 120:
            vx = dx / max(dist, 1) * self.speed * dt
            vy = dy / max(dist, 1) * self.speed * dt

            ox = self.sprite.center_x
            self.sprite.center_x += vx
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_x = ox

            oy = self.sprite.center_y
            self.sprite.center_y += vy
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_y = oy

        # ───── логика залпа ─────
        self.volley_timer -= dt

        if not self.in_volley and self.volley_timer <= 0 and dist < 600:
            self.in_volley = True
            self.volley_count = 0
            self.max_volley = random.randint(6, 10)
            self.volley_interval_timer = 0.0

        if self.in_volley:
            self.volley_interval_timer -= dt

            if self.volley_interval_timer <= 0:
                self.fire_arrow(player, projectile_list)
                self.volley_count += 1
                self.volley_interval_timer = self.volley_interval

                if self.volley_count >= self.max_volley:
                    self.in_volley = False
                    self.volley_timer = self.volley_cooldown

        # ───── флип спрайта ─────
        if dx > 0:
            self.sprite.scale_x = abs(self.sprite.scale_x)
        else:
            self.sprite.scale_x = -abs(self.sprite.scale_x)

        self.sprite.color = arcade.color.PURPLE_HEART

    def fire_arrow(self, player, projectile_list):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        dx /= max(dist, 1)
        dy /= max(dist, 1)

        arrow = arcade.Sprite("assets/arrow.png", scale=4)
        arrow.center_x = self.x
        arrow.center_y = self.y

        arrow.change_x = dx * 650
        arrow.change_y = dy * 650
        arrow.angle = math.degrees(math.atan2(dy, dx))

        arrow.damage = 14
        arrow.from_enemy = True

        projectile_list.append(arrow)
