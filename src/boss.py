import arcade
import math
import random
from settings import BOSS_HP, BOSS_SCALE, BOSS_SPEED
from enemy import Enemy, TankEnemy


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

        self.slowed = False
        self.slow_timer = 0.0
        self.slow_mult = 1.0

    @property
    def alive(self):
        return self.hp > 0

    def update_phase(self, player, walls, dt):
        if self.slowed:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slowed = False
                self.slow_mult = 1.0

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
            vx = dx / dist * (self.speed * speed_multiplier * (self.slow_mult ** 2)) * dt
            vy = dy / dist * (self.speed * speed_multiplier * (self.slow_mult ** 2)) * dt

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
            vx = dx / max(dist, 1) * self.speed * (self.slow_mult ** 2) * 0.4 * dt
            vy = dy / max(dist, 1) * self.speed * (self.slow_mult ** 2) * 0.4 * dt

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
                self.dash_speed = 1100 * self.slow_mult ** 2
            else:
                self.dash_time = 0.8
                self.dash_speed = 900 * self.slow_mult ** 2

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

class BossFloor2(Enemy):
    def __init__(self, x, y):
        try:
            self.sprite = arcade.Sprite("assets/boss_floor2.png", scale=7)
        except Exception:
            self.sprite = arcade.SpriteSolidColor(64, 64, arcade.color.DARK_RED)

        self.sprite.center_x = x
        self.sprite.center_y = y

        self.arrow_timer = 0.0

        self.hp = 1200
        self.max_hp = 1200
        self.speed = 90

        self.slowed = False
        self.slow_timer = 0.0
        self.slow_mult = 1.0

        self.state = "walk"   # walk | dash
        self.dash_timer = 0.0
        self.dash_dir = (0, 0)

        self.dash_cooldown = 0.0

    @property
    def alive(self):
        return self.hp > 0

    def update(self, player, walls, dt, projectile_list):
        if self.slowed:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slowed = False
                self.slow_mult = 1.0

        dx = player.x - self.sprite.center_x
        dy = player.y - self.sprite.center_y

        # кулдаун рывка
        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt

        if self.arrow_timer > 0:
            self.arrow_timer -= dt


        # ───────────── WALK ─────────────
        if self.state == "walk":
            dist = math.hypot(dx, dy)
            if dist > 1:
                vx = dx / dist * self.speed * (self.slow_mult ** 1.5) * dt
                vy = dy / dist * self.speed * (self.slow_mult ** 1.5) * dt

                ox = self.sprite.center_x
                self.sprite.center_x += vx
                if arcade.check_for_collision_with_list(self.sprite, walls):
                    self.sprite.center_x = ox

                oy = self.sprite.center_y
                self.sprite.center_y += vy
                if arcade.check_for_collision_with_list(self.sprite, walls):
                    self.sprite.center_y = oy

            # если на одной линии → рывок
            aligned_x = abs(dx) < 30
            aligned_y = abs(dy) < 30

            if (aligned_x or aligned_y) and self.dash_cooldown <= 0:
                if aligned_x:
                    self.dash_dir = (0, 1 if dy > 0 else -1)
                else:
                    self.dash_dir = (1 if dx > 0 else -1, 0)

                self.state = "dash"
                self.dash_timer = 0.9
                self.dash_cooldown = 5.0

        # ───────────── DASH ─────────────
        elif self.state == "dash":
            self.dash_timer -= dt

            vx = self.dash_dir[0] * 400 * (self.slow_mult ** 1.5) * dt
            vy = self.dash_dir[1] * 400 * (self.slow_mult ** 1.5) * dt

            old_x = self.sprite.center_x
            self.sprite.center_x += vx
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_x = old_x
                self.state = "walk"   # прерываем рывок

            old_y = self.sprite.center_y
            self.sprite.center_y += vy
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_y = old_y
                self.state = "walk"

            # разбрасываем стрелы в стороны
            if self.arrow_timer <= 0:
                self.spawn_side_arrows(projectile_list)
                self.arrow_timer = 0.19


            if self.dash_timer <= 0:
                self.state = "walk"

        # флип
        if dx > 0:
            self.sprite.scale_x = abs(self.sprite.scale_x)
        else:
            self.sprite.scale_x = -abs(self.sprite.scale_x)

    def spawn_side_arrows(self, projectile_list):
        px, py = self.sprite.center_x, self.sprite.center_y

        if self.dash_dir[0] != 0:
            dirs = [(0, 1), (0, -1)]
        else:
            dirs = [(1, 0), (-1, 0)]

        for dx, dy in dirs:
            arrow = arcade.Sprite("assets/arrow.png", scale=5)
            arrow.center_x = px
            arrow.center_y = py
            arrow.change_x = dx * 600
            arrow.change_y = dy * 600
            arrow.damage = 20
            arrow.from_enemy = True
            projectile_list.append(arrow)


class BossFloor3(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)

        # sprite (fallback to solid color if missing)
        try:
            self.sprite = arcade.Sprite("assets/boss_knight.png", scale=9)
        except Exception:
            self.sprite = arcade.SpriteSolidColor(80, 80, arcade.color.DARK_BLUE)

        self.sprite.center_x = x
        self.sprite.center_y = y

        # stats
        self.max_hp = 1000
        self.hp = self.max_hp
        self.speed = 90

        self.slowed = False
        self.slow_timer = 0.0
        self.slow_mult = 1.0

        self.phase = 1

        # shield / block
        self.blocking = False
        self.block_timer = 0.0

        # sword (telegraph + hit)
        self.sword_warning = False
        self.sword_timer = 0.0
        self.sword_range = 90
        self.sword_damage = 22
        self.sword_cooldown = 1.2
        self.sword_cd_timer = 0.0

        # circle arrows
        self.arrow_cd = 0.0
        self.arrow_interval = 4.0

        # summon tanks
        self.summon_cd = 10.0

        # dash in phase 2
        self.dash_cd = 0.0
        self.dashing = False
        self.dash_timer = 0.0
        self.dash_dx = 0.0
        self.dash_dy = 0.0
        self.dash_speed = 1600.0

    @property
    def x(self):
        return self.sprite.center_x

    @property
    def y(self):
        return self.sprite.center_y

    def take_damage(self, dmg):
        # boss ignores damage while blocking
        if self.blocking:
            return
        self.hp -= dmg

    def update_phase(self, player, walls, dt, enemies, enemy_projectiles):
        if self.slowed:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slowed = False
                self.slow_mult = 1.0
        # phase switch
        if self.hp <= self.max_hp * 0.5:
            self.phase = 2

        # cooldowns
        self.arrow_cd -= dt
        self.summon_cd -= dt
        self.block_timer -= dt
        self.dash_cd -= dt
        self.sword_cd_timer -= dt

        # random shield bursts
        if self.block_timer <= 0 and random.random() < 0.01:
            self.blocking = True
            self.block_timer = 1.2
        elif self.block_timer <= 0:
            self.blocking = False

        # ===== phase 2 dash: start dash when ready =====
        if self.phase == 2 and not self.dashing and self.dash_cd <= 0:
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.hypot(dx, dy)
            if dist > 300:
                self.dashing = True
                self.dash_timer = 0.2
                self.dash_dx = dx / max(dist, 1)
                self.dash_dy = dy / max(dist, 1)
                self.dash_cd = 5.0
                # reset arrow timer so arrows spawn during dash immediately
                self.arrow_cd = 0.0

        # handle active dash (movement + collision)
        if self.dashing:
            # move with collision checks
            vx = self.dash_dx * self.dash_speed * self.slow_mult * dt
            vy = self.dash_dy * self.dash_speed * self.slow_mult * dt

            old_x = self.sprite.center_x
            self.sprite.center_x += vx
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_x = old_x
                self.dashing = False

            old_y = self.sprite.center_y
            self.sprite.center_y += vy
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_y = old_y
                self.dashing = False

            # spawn side arrows at interval while dashing (handled by arrow_cd, see below)
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.dashing = False
            # return early so other actions (sword) don't trigger mid-dash
            # but allow arrow spawning below
        # ===== end dash =====

        # ===== sword telegraph / attack =====
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        # if close and sword off-cooldown, start telegraph
        if dist < self.sword_range and not self.sword_warning and self.sword_cd_timer <= 0:
            self.sword_warning = True
            self.sword_timer = 0.8

        if self.sword_warning:
            self.sword_timer -= dt
            if self.sword_timer <= 0:
                # perform hit if player still in range
                self.sword_warning = False
                self.sword_cd_timer = self.sword_cooldown
                if dist < self.sword_range:
                    # direct damage to player
                    player.hp -= self.sword_damage
                    # phase2 additional effect: apply burn on player by storing fields
                    if self.phase == 2:
                        # put burn on player: duration 4s, dps 2
                        # Player must have .burn_timer and .burn_dps (see suggested patch below)
                        if getattr(player, "burn_timer", 0) < 4.0:
                            player.burn_timer = 4.0
                            player.burn_dps = 2.0

        # ===== circle arrows =====
        if self.arrow_cd <= 0:
            ARROW_SPEED_LOCAL = 450
            ARROW_COUNT = 6
            for i in range(ARROW_COUNT):
                angle = 2 * math.pi * i / ARROW_COUNT
                dx_a = math.cos(angle)
                dy_a = math.sin(angle)

                arrow = arcade.Sprite("assets/arrow.png", scale=4)
                arrow.center_x = self.x
                arrow.center_y = self.y
                arrow.change_x = dx_a * ARROW_SPEED_LOCAL
                arrow.change_y = dy_a * ARROW_SPEED_LOCAL
                arrow.angle = math.degrees(math.atan2(dy_a, dx_a))
                arrow.damage = 10
                arrow.from_enemy = True
                # append into the window projectile list (enemy_projectiles)
                enemy_projectiles.append(arrow)
            self.arrow_cd = self.arrow_interval

        # ===== summon tanks =====
        if self.summon_cd <= 0:
            for _ in range(2):
                tx = int(self.x + random.randint(-60, 60))
                ty = int(self.y + random.randint(-60, 60))
                enemies.append(TankEnemy(tx, ty))
                # also register their sprite into enemy_sprites is handled by loader (if needed)
            self.summon_cd = 28.0

        # ===== movement when not too close =====
        if not self.dashing and dist > 80:
            vx = dx / max(dist, 1) * self.speed * self.slow_mult * dt
            vy = dy / max(dist, 1) * self.speed * self.slow_mult * dt

            old_x = self.sprite.center_x
            self.sprite.center_x += vx
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_x = old_x

            old_y = self.sprite.center_y
            self.sprite.center_y += vy
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_y = old_y

        # flip sprite to face player
        if dx > 0:
            self.sprite.scale_x = abs(self.sprite.scale_x)
        else:
            self.sprite.scale_x = -abs(self.sprite.scale_x)

        # visual feedback
        if self.blocking:
            self.sprite.color = arcade.color.BLUE
        elif self.phase == 2:
            self.sprite.color = arcade.color.RED_ORANGE
        else:
            self.sprite.color = arcade.color.WHITE