import arcade
import math
from settings import BOSS_HP, BOSS_SCALE, BOSS_SPEED
from enemy import Enemy


class Boss(Enemy):
    def __init__(self, x, y):
        # reuse enemy constructor but with boss sprite if exists
        try:
            self.sprite = arcade.Sprite("assets/boss.png", scale=BOSS_SCALE)
        except Exception:
            self.sprite = arcade.SpriteSolidColor(64, 64, arcade.color.PURPLE)
        self.sprite.center_x = x
        self.sprite.center_y = y

        self.is_dashing = False
        self.dash_time = 0.0
        self.dash_dir_x = 0.0
        self.dash_dir_y = 0.0

        self.dash_cooldown = 2.5 
        self.dash_speed = 700

        self.hp = BOSS_HP
        self.max_hp = BOSS_HP
        self.speed = BOSS_SPEED

        self.phase = 1

    @property
    def alive(self):
        return self.hp > 0

    def update_phase(self, player, walls, dt):

        # determine phase by hp ratio
        if self.phase == 1:
            desired_distance = 260
        elif self.phase == 2:
            desired_distance = 140
        else:
            desired_distance = 60

        hp_ratio = self.hp / self.max_hp if self.max_hp > 0 else 0.0

        if hp_ratio <= 0.33:
            self.phase = 3
        elif hp_ratio <= 0.66:
            self.phase = 2
        else:
            self.phase = 1

        self.dash_cooldown -= dt

        # boss behavior: slower or faster by phase
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 60 and dist > 1:
            speed_multiplier = {1: 0.6, 2: 1.0, 3: 1.6}[self.phase]
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
        
        else:
            # небольшое давление на игрока вблизи
            vx = dx / max(dist, 1) * self.speed * 0.4 * dt
            vy = dy / max(dist, 1) * self.speed * 0.4 * dt

            old_x = self.sprite.center_x
            self.sprite.center_x += vx
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_x = old_x

            old_y = self.sprite.center_y
            self.sprite.center_y += vy

            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_y = old_y


        if not self.is_dashing and self.phase >= 2 and self.dash_cooldown <= 0 and dist > 120:
            self.is_dashing = True

            # фиксируем направление рывка
            self.dash_dir_x = dx / max(dist, 1)
            self.dash_dir_y = dy / max(dist, 1)

            # параметры рывка по фазам
            if self.phase == 3:
                self.dash_time = 1.1
                self.dash_speed = 1100
            else:
                self.dash_time = 0.8
                self.dash_speed = 900

            self.dash_cooldown = 2.5

        if self.is_dashing:
            self.dash_time -= dt

            vx = self.dash_dir_x * self.dash_speed * dt
            vy = self.dash_dir_y * self.dash_speed * dt

            old_x = self.sprite.center_x
            self.sprite.center_x += vx
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_x = old_x

            old_y = self.sprite.center_y
            self.sprite.center_y += vy
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_y = old_y

            if self.dash_time <= 0:
                self.is_dashing = False

        # flip sprite
        if dx > 0:
            self.sprite.scale_x = abs(self.sprite.scale_x)
        else:
            self.sprite.scale_x = -abs(self.sprite.scale_x)

        if self.phase == 3:
            self.sprite.color = arcade.color.RED_ORANGE
        elif self.phase == 2:
            self.sprite.color = arcade.color.ORANGE
        else:
            self.sprite.color = arcade.color.WHITE

