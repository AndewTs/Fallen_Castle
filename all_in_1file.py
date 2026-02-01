import arcade
import math
import random

# ================= НАСТРОЙКИ =================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Pixel Dungeon — MVP with Treasure"

PLAYER_SPEED = 320
PLAYER_HP = 400
PLAYER_SCALE = 7

ENEMY_SCALE = 6
ENEMY_HP = 100
ENEMY_SPEED = 140

BOSS_SCALE = 0.09
BOSS_HP = 1000
BOSS_SPEED = 110

PIXEL = 6  # used for pixel-draw heart etc (optional)

SWORD_LENGTH = 100
SWORD_THICKNESS = 5
SWORD_TIME = 0.12

MAX_FLOORS = 3
BASE_FLOOR_SIZE = 3

ROOM_GRID_SIZE = 3  # size x size rooms

# door directions
DIRECTIONS = {
    "up": (0, 1),
    "down": (0, -1),
    "left": (-1, 0),
    "right": (1, 0)
}

OPPOSITE = {
    "up": "down",
    "down": "up",
    "left": "right",
    "right": "left"
}

# chance that a cleared normal room drops a key (0..1)
KEY_DROP_CHANCE = 0.25

# wall tile
WALL_TILE = 64

# projectile speed for bow
ARROW_SPEED = 700.0

HALBERD_RADIUS = 200
HALBERD_ARC_ANGLE = 65  # градусов
HALBERD_DAMAGE = 100
HALBERD_TIME = 0.22
HALBERD_COOLDOWN = 0.45

HAMMER_RADIUS = 140
HAMMER_DAMAGE = 180
HAMMER_TIME = 0.18
HAMMER_COOLDOWN = 0.75
HAMMER_WINDUP = 0.25     # задержка перед ударом
HAMMER_IMPACT = 0.15    # вспышка удара
HAMMER_SHAKE = 8        # сила тряски экрана
HAMMER_STUN_TIME = 1.2
HAMMER_BOSS_SLOW_MULT = 0.5   # 50% скорости
HAMMER_BOSS_SLOW_TIME = 2.5  # секунды



# ====================== HELPERS ======================
def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

# ====================== ROOM & FLOOR ======================
class Room:
    def __init__(self, pos, room_type="normal"):
        """
        pos: (x, y) tuple
        room_type: "start", "normal", "boss", "treasure"
        """
        self.pos = pos
        self.type = room_type
        self.doors = {}  # filled by Floor: {"up": (x,y), ...}
        self.enemy_spawns = []  # list of dicts {"type":"enemy","x":int,"y":int}
        self.walls = []  # optional positions of obstacles (not sprites)
        self.forbidden_zones = []  # list of (x,y,radius)
        self.treasure_unlocked = False  # for treasure rooms

        # enemy count by type
        if self.type == "start":
            cnt = 0
        elif self.type == "boss":
            cnt = 0
        elif self.type == "treasure":
            cnt = 0
        else:
            cnt = random.randint(2, 4)

        # generate spawns (positions will be used when loading)
        for _ in range(cnt):
            ex = random.randint(200, 1080)
            ey = random.randint(220, 620)
            self.enemy_spawns.append({"type": "enemy", "x": ex, "y": ey, "hp": None})

    def set_doors(self, doors_dict):
        self.doors = doors_dict

    def add_forbidden_zone(self, x, y, radius):
        self.forbidden_zones.append((x, y, radius))


class Floor:
    def __init__(self, floor_number=1):
        self.floor_number = floor_number
        self.size = BASE_FLOOR_SIZE + (floor_number - 1)
        size = self.size
        self.rooms = {}  # dict[(x,y)] = Room
        self.start_pos = (0, 0)
        self.boss_pos = (size - 1, size - 1)
        self.current_pos = self.start_pos
        self.treasure_pos = None
        self.generate()

    def generate(self):
        # create rooms
        for x in range(self.size):
            for y in range(self.size):
                pos = (x, y)
                if pos == self.start_pos:
                    r = Room(pos, "start")
                elif pos == self.boss_pos:
                    r = Room(pos, "boss")
                else:
                    r = Room(pos, "normal")
                self.rooms[pos] = r

        # pick one random normal room to be treasure (not start, not boss)
        normal_positions = [p for p, r in self.rooms.items() if r.type == "normal"]
        if normal_positions:
            tp = random.choice(normal_positions)
            self.rooms[tp].type = "treasure"
            self.rooms[tp].treasure_unlocked = False
            self.treasure_pos = tp

        # connect doors (4-neighbors)
        for (x, y), room in list(self.rooms.items()):
            doors = {}
            for name, (dx, dy) in DIRECTIONS.items():
                npos = (x + dx, y + dy)
                if npos in self.rooms:
                    doors[name] = npos
            room.set_doors(doors)

        # Add forbidden zones for doors & start
        SCREEN_W = SCREEN_WIDTH
        SCREEN_H = SCREEN_HEIGHT
        DOOR_MARGIN = 140
        for (x, y), room in self.rooms.items():
            if "up" in room.doors:
                room.add_forbidden_zone(SCREEN_W // 2, SCREEN_H - 80, DOOR_MARGIN)
            if "down" in room.doors:
                room.add_forbidden_zone(SCREEN_W // 2, 80, DOOR_MARGIN)
            if "left" in room.doors:
                room.add_forbidden_zone(80, SCREEN_H // 2, DOOR_MARGIN)
            if "right" in room.doors:
                room.add_forbidden_zone(SCREEN_W - 80, SCREEN_H // 2, DOOR_MARGIN)
            if room.type == "start":
                room.add_forbidden_zone(SCREEN_W // 2, 190, 200)

    def get_current_room(self):
        return self.rooms[self.current_pos]

    def move(self, pos):
        if pos in self.rooms:
            self.current_pos = pos
            return True
        return False

# ====================== ENTITIES ======================
class Player:
    def __init__(self, x, y):
        # try to load sprite, fallback to solid color
        self.burn_timer = 0.0
        self.burn_dps = 0.0

        self.slow_timer = 0.0
        self.base_speed = PLAYER_SPEED

        # ───── активный предмет: щит ─────
        self.has_shield = False
        self.shield_ready = False
        self.shield_room_cooldown = 1
        self.parry_window = 2   
        self.parry_timer = 0.0
        self.parry_active = False
        self.shield_radius = 140


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
        self.weapon = "sword"

        # keys count
        self.keys = 0

        # attack timer
        self.attack_cooldown = 0.25
        self.attack_timer = 0.0
        self.shield_time_cooldown = 0.0

        self.dash_cooldown = 0.0
        self.dash_cd_time = 1.2      # перезарядка
        self.dash_time = 0.0
        self.dash_duration = 0.18
        self.dash_speed = 1200
        self.dash_dx = 0
        self.dash_dy = 0

    @property
    def x(self):
        return self.sprite.center_x

    @property
    def y(self):
        return self.sprite.center_y

    def update(self, dt, keys_held):
        # reduce attack timer
        if self.slow_timer > 0:
            self.slow_timer -= dt
            self.speed = self.base_speed * 0.4
        else:
            self.speed = self.base_speed


        if self.attack_timer > 0:
            self.attack_timer -= dt

        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt

        if self.burn_timer > 0:
            self.burn_timer -= dt
            self.hp -= self.burn_dps * dt
            if self.burn_timer <= 0:
                self.burn_dps = 0.0
        
        if self.burn_timer > 0:
            self.sprite.color = arcade.color.ORANGE
        elif self.burn_timer == 0:
            self.sprite.color = arcade.color.LIGHT_GRAY

        if self.parry_timer > 0:
            self.parry_timer -= dt
            if self.parry_timer <= 0:
                self.parry_active = False


    def can_attack(self):
        return self.attack_timer <= 0

    def reset_attack(self):
        self.attack_timer = self.attack_cooldown

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


# ====================== WINDOW ======================
class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.current_floor = 1

        # player and spritelists
        self.player = Player(SCREEN_WIDTH // 2, 120)
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player.sprite)

        self.enemy_sprites = arcade.SpriteList()
        self.wall_sprites = arcade.SpriteList()
        self.door_sprites = arcade.SpriteList()

        self.screen_shake = 0

        self.projectile_sprites = arcade.SpriteList()  # arrows etc
        self.pickup_sprites = arcade.SpriteList()      # keys / weapons in room

        # floor / rooms
        self.floor = Floor(self.current_floor)
        self.current_pos = self.floor.current_pos

        # runtime entity objects for the current room
        self.current_enemies = []  # list of Enemy/Boss instances

        # attack visuals (directional sword slashes)
        self.slashes = []  # dicts with x1,y1,x2,y2,time,width

        # axe swings (circular AoE)
        self.axe_swings = []  # dicts with x,y,radius,time,damage
        self.halberd_swings = []  
        self.hammer_swings = []



        # input
        self.keys_held = set()

        # room state
        self.room_cleared = False

        # transient notice
        self.notice_text = ""
        self.notice_timer = 0.0

        # load first room
        self.load_current_room()

    # ----------------------
    # HELPERS
    # ----------------------
    def try_enter_door(self):
        # ❗ ЗАПРЕТ: комната не зачищена
        if not self.room_cleared:
            self.notice_text = "Defeat all enemies first!"
            self.notice_timer = 1.5
            return

    # проверяем двери рядом с игроком
        for door in self.door_sprites:
            if arcade.get_distance_between_sprites(self.player.sprite, door) < 90:
                direction = door.direction
                room = self.floor.get_current_room()

                if direction in room.doors:
                    new_pos = room.doors[direction]
                    self.floor.current_pos = new_pos
                    self.load_current_room()
                    return


    def try_activate_shield(self):
        p = self.player

        if not p.has_shield:
            return

        if not p.shield_ready:
            return
        
        p.parry_active = True
        p.parry_timer = p.parry_window

        # уничтожаем стрелы врагов
        for arrow in self.projectile_sprites[:]:
            if not getattr(arrow, "from_enemy", False):
                continue

            dx = arrow.center_x - p.x
            dy = arrow.center_y - p.y
            dist = math.hypot(dx, dy)

            if dist <= p.shield_radius:
                arrow.remove_from_sprite_lists()

        # уходим на перезарядку
        p.shield_ready = False

        room = self.floor.get_current_room()
        if room.type == "boss":
            p.shield_time_cooldown = 7.0
        else:
            p.shield_room_cooldown = 2
    
    def find_free_position(self, min_x=150, max_x=None, min_y=150, max_y=None, tries=100):
        if max_x is None:
            max_x = SCREEN_WIDTH - 150
        if max_y is None:
            max_y = SCREEN_HEIGHT - 150

        for _ in range(tries):
            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)

            dummy = arcade.SpriteSolidColor(90, 90, arcade.color.RED)
            dummy.center_x = x
            dummy.center_y = y

            if not arcade.check_for_collision_with_list(dummy, self.wall_sprites) and \
               not arcade.check_for_collision_with_list(dummy, self.door_sprites) and \
               not arcade.check_for_collision_with_list(dummy, self.pickup_sprites):
                return x, y

        return SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

    # ----------------------
    # room loading / spawn
    # ----------------------
    def load_current_room(self):
        # clear previous
        self.enemy_sprites.clear()
        self.wall_sprites.clear()
        self.door_sprites.clear()
        self.pickup_sprites.clear()
        self.projectile_sprites.clear()
        self.current_enemies.clear()
        self.slashes.clear()
        self.axe_swings.clear()
        self.room_cleared = False
        self.notice_text = ""
        self.notice_timer = 0.0

        room = self.floor.get_current_room()

        # forbidden zones for this room are already populated by Floor during generate()
        # ensure player spawn zone exists
        room.add_forbidden_zone(SCREEN_WIDTH // 2, 190, 200)

        # spawn walls: border + some rocks
        # top/bottom rows
        for x in range(0, SCREEN_WIDTH, WALL_TILE):
            # bottom
            rock = arcade.SpriteSolidColor(WALL_TILE, WALL_TILE, arcade.color.DARK_BROWN)
            rock.is_rock = False
            rock.is_wall = True
            rock.center_x = x + WALL_TILE // 2
            rock.center_y = WALL_TILE // 2
            self.wall_sprites.append(rock)
            # top
            rock2 = arcade.SpriteSolidColor(WALL_TILE, WALL_TILE, arcade.color.DARK_BROWN)
            rock.is_rock = False
            rock.is_wall = True
            rock2.center_x = x + WALL_TILE // 2
            rock2.center_y = SCREEN_HEIGHT - WALL_TILE // 2
            self.wall_sprites.append(rock2)
        # left/right
        for y in range(WALL_TILE, SCREEN_HEIGHT - WALL_TILE, WALL_TILE):
            rock = arcade.SpriteSolidColor(WALL_TILE, WALL_TILE, arcade.color.DARK_BROWN)
            rock.is_rock = False
            rock.is_wall = True
            rock.center_x = WALL_TILE // 2
            rock.center_y = y + WALL_TILE // 2
            self.wall_sprites.append(rock)
            rock2 = arcade.SpriteSolidColor(WALL_TILE, WALL_TILE, arcade.color.DARK_BROWN)
            rock.is_rock = False
            rock.is_wall = True
            rock2.center_x = SCREEN_WIDTH - WALL_TILE // 2
            rock2.center_y = y + WALL_TILE // 2
            self.wall_sprites.append(rock2)

        # spawn obstacles inside room (a few rocks), avoid forbidden zones
        def is_position_allowed(x, y, forbidden):
            for fx, fy, r in forbidden:
                if abs(x - fx) < r and abs(y - fy) < r:
                    return False
            return True

        attempts = 0
        spawned = 0
        if room.type not in ('boss', 'start', 'treasure'):
            while spawned < 6 and attempts < 10:
                attempts += 1
                x = random.randint(180, SCREEN_WIDTH - 180)
                y = random.randint(180, SCREEN_HEIGHT - 180)

                if not is_position_allowed(x, y, room.forbidden_zones):
                    continue

                rock = arcade.Sprite("assets/rock.png", scale=6.0)
                rock.center_x = x
                rock.center_y = y

                rock.is_rock = True        
                rock.is_wall = False

                self.wall_sprites.append(rock)

        # spawn doors (sprites) - do this early so find_free_position avoids doors
        margin = 80

        def spawn_door(x, y, direction):
            # create a door sprite (simple solid color if asset missing)
            try:
                d = arcade.Sprite("assets/door.png", scale=6.0)
            except Exception:
                d = arcade.SpriteSolidColor(120, 160, arcade.color.DARK_BROWN)
            d.center_x = x
            d.center_y = y
            d.direction = direction
            # make an appropriate hit box (using default is fine)
            self.door_sprites.append(d)

        if room.doors.get("up") is not None:
            spawn_door(SCREEN_WIDTH // 2, SCREEN_HEIGHT - margin, "up")
        if room.doors.get("down") is not None:
            spawn_door(SCREEN_WIDTH // 2, margin, "down")
        if room.doors.get("left") is not None:
            spawn_door(margin, SCREEN_HEIGHT // 2, "left")
        if room.doors.get("right") is not None:
            spawn_door(SCREEN_WIDTH - margin, SCREEN_HEIGHT // 2, "right")

        # spawn enemies from room.enemy_spawns (but only after walls & doors exist)
        if room.type == "boss":
            bx = SCREEN_WIDTH // 2
            by = SCREEN_HEIGHT // 2 + 60

            if self.current_floor == 1:
                boss = Boss(bx, by)
            elif self.current_floor == 2:
                boss = BossFloor2(bx, by)
            elif self.current_floor == 3:
                boss = BossFloor3(bx, by)

            self.current_enemies.append(boss)
            self.enemy_sprites.append(boss.sprite)
        else:
            for spawn in room.enemy_spawns:
                x, y = self.find_free_position()
                roll = random.random()
                if self.current_floor == 1:
                    if roll < 0.5:
                        e = Enemy(x, y)
                    elif roll < 0.7:
                        e = FastEnemy(x, y)
                    elif roll < 0.9:
                        e = TankEnemy(x, y)
                    else:
                        e = RangedEnemy(x, y)
                
                if self.current_floor == 2:
                    if roll < 0.35:
                        e = EliteRunner(x, y)
                    elif roll < 0.65:
                        e = EliteShooter(x, y)
                    elif roll < 0.85:
                        e = FastEnemy(x, y)
                    else:
                        e = Enemy(x, y)

                if self.current_floor == 3:
                    roll = random.random()
                    if roll < 0.25:
                        e = EliteTankFloor3(x, y)
                    elif roll < 0.4:
                        e = EliteArcherFloor3(x, y)
                    elif roll < 0.5:
                        e = TankEnemy(x, y)
                    elif roll < 0.75:
                        e = EliteShooter(x, y)
                    else:
                        e = FastEnemy(x, y)

                self.current_enemies.append(e)
                self.enemy_sprites.append(e.sprite)

        # if this is a treasure room and it's unlocked, spawn weapons as pickups
        if room.type == "treasure" and room.treasure_unlocked:
            # spawn axe pickup
            ax = arcade.SpriteSolidColor(28, 28, arcade.color.DARK_ORANGE)
            ax.center_x, ax.center_y = self.find_free_position()
            ax.pickup_type = "axe"
            self.pickup_sprites.append(ax)

            # spawn bow pickup
            bw = arcade.SpriteSolidColor(28, 28, arcade.color.DARK_GREEN)
            bw.center_x, bw.center_y = self.find_free_position()
            bw.pickup_type = "bow"
            self.pickup_sprites.append(bw)

            if self.current_floor >= 2:
                shield = arcade.SpriteSolidColor(28, 28, arcade.color.DARK_GREEN)
                shield.center_x, shield.center_y = self.find_free_position()
                shield.pickup_type = "shield"
                self.pickup_sprites.append(shield)

                halberd = arcade.SpriteSolidColor(32, 32, arcade.color.LIGHT_BLUE)
                halberd.center_x, halberd.center_y = self.find_free_position()
                halberd.pickup_type = "halberd"
                self.pickup_sprites.append(halberd)

                roll = random.random()
                if roll > 0.8:
                    hm = arcade.SpriteSolidColor(32, 32, arcade.color.LIGHT_BLUE)
                    hm.center_x, halberd.center_y = self.find_free_position()
                    hm.pickup_type = "hammer"
                    self.pickup_sprites.append(hm)
            


        # room cleared flag
        self.room_cleared = len(self.current_enemies) == 0

        # teleport player to entrance side (simple)
        self.player.sprite.center_x = SCREEN_WIDTH // 2
        self.player.sprite.center_y = 190
        
        player = self.player

        if player.has_shield and not player.shield_ready:
            player.shield_room_cooldown -= 1
            if player.shield_room_cooldown <= 0:
                player.shield_ready = True


    # ----------------------
    # drawing
    # ----------------------
    def on_draw(self):
        self.clear()

        # floor background
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.DARK_SLATE_GRAY)

        # walls, doors, enemies, pickups, player, projectiles
        self.wall_sprites.draw(pixelated=True)
        self.door_sprites.draw(pixelated=True)
        self.enemy_sprites.draw(pixelated=True)
        self.pickup_sprites.draw(pixelated=True)
        self.projectile_sprites.draw(pixelated=True)
        self.player_list.draw(pixelated=True)

        if self.player.has_shield and self.player.shield_ready:
            arcade.draw_circle_outline(
                self.player.x,
                self.player.y,
                self.player.shield_radius,
                arcade.color.CYAN,
                3
            )

        # draw slashes
        for s in self.slashes:
            arcade.draw_line(s["x1"], s["y1"], s["x2"], s["y2"], arcade.color.WHITE, s["width"])

        # draw axe swings (circle)
        for a in self.axe_swings:
            arcade.draw_circle_outline(a["x"], a["y"], a["radius"], arcade.color.ORANGE, 3)

        for h in self.halberd_swings:
            arcade.draw_arc_outline(
                h["x"],
                h["y"],
                h["radius"] * 2,
                h["radius"] * 2,
                arcade.color.LIGHT_BLUE,
                h["angle"] - h["arc"] / 2,
                h["angle"] + h["arc"] / 2,
                4
            )

        for h in self.hammer_swings:
            if h["phase"] == "windup":
                arcade.draw_circle_outline(
                    h["x"], h["y"],
                    h["radius"],
                    arcade.color.ORANGE,
                    3
                )
            else:
                arcade.draw_circle_filled(
                    h["x"], h["y"],
                    h["radius"],
                    (*arcade.color.ORANGE[:3], 120)
                )


        # HUD
        arcade.draw_text(f"HP: {int(self.player.hp)}/{self.player.max_hp}", 12, SCREEN_HEIGHT - 28, arcade.color.BLACK, 18)
        arcade.draw_text(f"Room: {self.floor.current_pos}", 12, SCREEN_HEIGHT - 54, arcade.color.BLACK, 14)
        arcade.draw_text(f"Keys: {self.player.keys}", 12, SCREEN_HEIGHT - 78, arcade.color.GOLD, 14)
        arcade.draw_text(f"Weapon: {self.player.weapon}", 12, SCREEN_HEIGHT - 102, arcade.color.LIGHT_GRAY, 14)
        if self.player.has_shield and not self.player.shield_ready:
            room = self.floor.get_current_room()
            if room.type == "boss":
                arcade.draw_text(
                    f"Shield CD: {int(self.player.shield_time_cooldown)}s",
                    12, SCREEN_HEIGHT - 126,
                    arcade.color.CYAN, 14
                )


        arcade.draw_text(
                f"Floor: {self.current_floor}",
                SCREEN_WIDTH - 160, SCREEN_HEIGHT - 28,
                arcade.color.BLACK, 16
                        )


        for e in self.current_enemies:
            if isinstance(e, Boss):
                arcade.draw_text(
                    f"PHASE {e.phase}",
                    e.x - 30, e.y + 60,
                    arcade.color.RED, 14
                )
        
        for e in self.current_enemies:
            if isinstance(e, BossFloor3) and e.sword_warning:
                dx = self.player.x - e.x
                dy = self.player.y - e.y

                angle = math.degrees(math.atan2(dy, dx))
    
                arcade.draw_arc_outline(
                    e.x,
                    e.y,
                    e.sword_range * 2,
                    e.sword_range * 2,
                    arcade.color.RED,
                    angle - 60,
                    angle + 60,
                    5
                )
        
        for e in self.current_enemies:
            if isinstance(e, EliteTankFloor3) and e.is_slamming:
                arcade.draw_circle_outline(
                    e.x,
                    e.y,
                    e.slam_radius,
                    arcade.color.RED,
                    4
                )
        
            if isinstance(e, EliteArcherFloor3) and e.in_volley:
                arcade.draw_circle_outline(
                    e.x,
                    e.y,
                    30,
                    arcade.color.ORANGE,
                    3       
                )
            if getattr(e, "stunned", False):
                arcade.draw_circle_outline(
                    e.x,
                    e.y + 20,
                    20,
                arcade.color.YELLOW,
                    2
                )
            if getattr(e, "slowed", False):
                arcade.draw_circle_outline(
                    e.x,
                    e.y,
                    36,
                    arcade.color.BLUE,
                    3
                )





        # notice text
        if self.notice_timer > 0 and self.notice_text:
            arcade.draw_text(self.notice_text, SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 40, arcade.color.YELLOW, 20)

        if self.room_cleared:
            arcade.draw_text("Press E near a door to enter", SCREEN_WIDTH//2 - 160, 24, arcade.color.WHITE, 14)

    # ----------------------
    # update
    # ----------------------
    def on_update(self, dt):
        # movement - read keys
        if self.player.dash_time > 0:
            self.player.dash_time -= dt

            vx = self.player.dash_dx * self.player.dash_speed * dt
            vy = self.player.dash_dy * self.player.dash_speed * dt

            old_x = self.player.sprite.center_x
            self.player.sprite.center_x += vx
            if arcade.check_for_collision_with_list(self.player.sprite, self.wall_sprites):
                self.player.sprite.center_x = old_x

            old_y = self.player.sprite.center_y
            self.player.sprite.center_y += vy
            if arcade.check_for_collision_with_list(self.player.sprite, self.wall_sprites):
                self.player.sprite.center_y = old_y

        dx = dy = 0
        if arcade.key.W in self.keys_held:
            dy += 1
        if arcade.key.S in self.keys_held:
            dy -= 1
        if arcade.key.A in self.keys_held:
            dx -= 1
        if arcade.key.D in self.keys_held:
            dx += 1

        # normalize
        if dx or dy:
            length = math.hypot(dx, dy)
            if length == 0:
                length = 1
            nx = dx / length
            ny = dy / length

            # move with collision separately per axis
            old_x = self.player.sprite.center_x
            self.player.sprite.center_x += nx * self.player.speed * dt
            if arcade.check_for_collision_with_list(self.player.sprite, self.wall_sprites):
                self.player.sprite.center_x = old_x

            old_y = self.player.sprite.center_y
            self.player.sprite.center_y += ny * self.player.speed * dt
            if arcade.check_for_collision_with_list(self.player.sprite, self.wall_sprites):
                self.player.sprite.center_y = old_y

            # flip sprite
            if nx > 0:
                self.player.sprite.scale_x = abs(self.player.sprite.scale_x)
            elif nx < 0:
                self.player.sprite.scale_x = -abs(self.player.sprite.scale_x)

        # update player timers
        self.player.update(dt, self.keys_held)
        p = self.player
        room = self.floor.get_current_room()

        if p.has_shield and not p.shield_ready:
            if room.type == "boss":
                p.shield_time_cooldown -= dt
                if p.shield_time_cooldown <= 0:
                    p.shield_ready = True


        # update enemies
        for e in list(self.current_enemies):
            if isinstance(e, Boss):
                e.update_phase(self.player, self.wall_sprites, dt)
            elif isinstance(e, BossFloor2):
                e.update(self.player, self.wall_sprites, dt, self.projectile_sprites)
            elif isinstance(e, BossFloor3):
                new_enemies = []
                e.update_phase(
                    player=self.player,
                    walls=self.wall_sprites,
                    dt=dt,
                    enemies=new_enemies,                 # ← сюда босс добавляет танков
                    enemy_projectiles=self.projectile_sprites   # ← сюда босс добавляет стрелы
                )
                if len(new_enemies) > 0:
                    for ne in new_enemies:
                        self.current_enemies.append(ne)
                        self.enemy_sprites.append(ne.sprite)
                    new_enemies.clear()
            elif isinstance(e, RangedEnemy):
                e.update(self.player, self.wall_sprites, dt, self.projectile_sprites)
            elif isinstance(e, EliteShooter):
                e.update(self.player, self.wall_sprites, dt, self.projectile_sprites)
            elif isinstance(e, EliteArcherFloor3):
                e.update(self.player, self.wall_sprites, dt, self.projectile_sprites)
            else:
                e.update(self.player, self.wall_sprites, dt)
            # simple contact damage
            if abs(e.x - self.player.x) < 28 and abs(e.y - self.player.y) < 28:
                self.player.hp -= 20 * dt

            if not e.alive:
                # remove
                try:
                    self.current_enemies.remove(e)
                except ValueError:
                    pass
                try:
                    self.enemy_sprites.remove(e.sprite)
                except ValueError:
                    pass

        # update projectiles (arrows)
        for proj in list(self.projectile_sprites):
            proj.center_x += proj.change_x * dt
            proj.center_y += proj.change_y * dt

            # collision with enemies (ТОЛЬКО для стрел игрока)d
            if not getattr(proj, "from_enemy", False):
                for e in list(self.current_enemies):
                    if arcade.check_for_collision(proj, e.sprite):
                        e.hp -= getattr(proj, "damage", 40)
                        try:
                                self.projectile_sprites.remove(proj)
                        except ValueError:
                            pass
                        break

            if getattr(proj, "from_enemy", False):
                if arcade.check_for_collision(proj, self.player.sprite):

                    if self.player.parry_active:

                        proj.from_enemy = False
                        proj.change_x *= -1
                        proj.change_y *= -1
                        proj.damage = int(proj.damage * 1.5)

                        proj.color = arcade.color.CYAN

                        self.player.parry_active = False
                        self.player.parry_timer = 0
                    else:
                        self.player.hp -= getattr(proj, "damage", 15)
                        self.projectile_sprites.remove(proj)

                    continue



            # collision with walls
            if arcade.check_for_collision_with_list(proj, self.wall_sprites):
                try:
                    self.projectile_sprites.remove(proj)
                except ValueError:
                    pass
                continue
            

            # out of bounds
            if proj.center_x < -200 or proj.center_x > SCREEN_WIDTH + 200 or proj.center_y < -200 or proj.center_y > SCREEN_HEIGHT + 200:
                try:
                    self.projectile_sprites.remove(proj)
                except ValueError:
                    pass

        # project slashes lifetime
        for s in list(self.slashes):
            s["time"] -= dt
            if s["time"] <= 0:
                self.slashes.remove(s)

        # axe swings lifetime and apply damage once
        for a in list(self.axe_swings):
            # apply damage to enemies within radius immediately when created
            if a.get("applied", False) is False:
                for e in list(self.current_enemies):
                    if distance((e.x, e.y), (a["x"], a["y"])) <= a["radius"]:
                        e.hp -= a.get("damage", 60)
                a["applied"] = True

            a["time"] -= dt
            if a["time"] <= 0:
                self.axe_swings.remove(a)

        for h in list(self.halberd_swings):
            if not h["applied"]:
                for e in self.current_enemies:
                    dx = e.x - h["x"]
                    dy = e.y - h["y"]
                    dist = math.hypot(dx, dy)

                    if dist > h["radius"]:
                        continue

                    enemy_angle = math.degrees(math.atan2(dy, dx))
                    delta = (enemy_angle - h["angle"] + 180) % 360 - 180

                    if abs(delta) <= h["arc"] / 2:
                        e.hp -= h["damage"]

                h["applied"] = True

            h["time"] -= dt
            if h["time"] <= 0:
                self.halberd_swings.remove(h)

        for h in list(self.hammer_swings):
            h["timer"] -= dt

            if h["phase"] == "windup" and h["timer"] <= HAMMER_IMPACT:
                # ───── МОМЕНТ УДАРА ─────
                h["phase"] = "impact"


                # урон врагам
                for e in self.current_enemies:
                    if arcade.get_distance_between_sprites(e.sprite, self.player.sprite) <= h["radius"]:
                        e.hp -= h["damage"]

                    # обычные враги — стан
                        if getattr(e, "can_be_stunned", True):                         
                            e.stunned = True
                            e.stun_timer = HAMMER_STUN_TIME

                        else:
                            e.slowed = True
                            e.slow_timer = HAMMER_BOSS_SLOW_TIME
                            e.slow_mult = HAMMER_BOSS_SLOW_MULT


                # ломаем камни
                for obj in self.wall_sprites[:]:
                    if not getattr(obj, "is_rock", False):
                        continue

                    if arcade.get_distance_between_sprites(obj, self.player.sprite) <= h["radius"]:
                        obj.remove_from_sprite_lists()
            if h["timer"] <= 0:
                self.hammer_swings.remove(h)




        # pickups: keys and weapons
        for p in list(self.pickup_sprites):
            if arcade.check_for_collision(self.player.sprite, p):
                ptype = getattr(p, "pickup_type", "key")
                if ptype == "key":
                    self.player.keys += 1
                    self.notice_text = "Picked up a key!"
                    self.notice_timer = 2.0
                elif ptype == "axe":
                    self.player.weapon = "axe"
                    self.notice_text = "Picked up: Axe"
                    self.notice_timer = 2.0
                elif ptype == "bow":
                    self.player.weapon = "bow"
                    self.notice_text = "Picked up: Bow"
                    self.notice_timer = 2.0
                elif ptype == "shield":
                    self.player.has_shield = True
                    self.notice_text = "Picked up: Shield"
                    self.notice_timer = 2.0
                elif ptype == "halberd":
                    self.player.weapon = "halberd"
                    self.notice_text = "Picked up: Halberd"
                    self.notice_timer = 2.0

                elif ptype == "hammer":
                    self.player.weapon = "hammer"
                    self.notice_text = "Picked up: Battle Hammer"
                    self.notice_timer = 2.0

                try:
                    self.pickup_sprites.remove(p)
                except ValueError:
                    pass

        # room cleared?
        prev_cleared = self.room_cleared
        self.room_cleared = len(self.current_enemies) == 0

        room = self.floor.get_current_room()

        if self.room_cleared and room.type == "boss":
            if self.current_floor < MAX_FLOORS:
                self.current_floor += 1
                self.notice_text = f"Floor {self.current_floor}"
                self.notice_timer = 2.5

                self.floor = Floor(self.current_floor)
                self.player.sprite.center_x = SCREEN_WIDTH // 2
                self.player.sprite.center_y = 120
                self.load_current_room()
            else:
                self.notice_text = "YOU WIN!"
                self.notice_timer = 999

        # if we have newly cleared a normal room (not start/boss/treasure), maybe drop a key
        room = self.floor.get_current_room()
        if self.room_cleared and (not prev_cleared):
            # newly cleared
            if room.type not in ('start', 'boss', 'treasure'):
                if random.random() < KEY_DROP_CHANCE:
                    # spawn a key pickup
                    kx, ky = self.find_free_position()
                    key_sprite = arcade.SpriteSolidColor(24, 18, arcade.color.GOLD)
                    key_sprite.center_x = kx
                    key_sprite.center_y = ky
                    key_sprite.pickup_type = "key"
                    self.pickup_sprites.append(key_sprite)
                    self.notice_text = "A key dropped!"
                    self.notice_timer = 2.0

        # notice timer
        if self.notice_timer > 0:
            self.notice_timer -= dt
            if self.notice_timer <= 0:
                self.notice_text = ""

        # if player died -> reset floor
        if self.player.hp <= 0:
            # пересоздаём этаж
            self.current_floor = 1
            self.floor = Floor(self.current_floor)
            self.floor.current_pos = self.floor.start_pos

            # пересоздаём игрока
            self.player = Player(SCREEN_WIDTH // 2, 120)
            self.player_list.clear()
            self.player_list.append(self.player.sprite)

            # загружаем стартовую комнату
            self.load_current_room()
            return
        

    # ----------------------
    # input
    # ----------------------
    def on_key_press(self, key, modifiers):
        # add to held keys
        self.keys_held.add(key)

        if key == arcade.key.LSHIFT:
            if self.player.dash_cooldown <= 0:
                dx = dy = 0
                if arcade.key.W in self.keys_held:
                    dy += 1
                if arcade.key.S in self.keys_held:
                    dy -= 1
                if arcade.key.A in self.keys_held:
                    dx -= 1
                if arcade.key.D in self.keys_held:
                    dx += 1

                if dx != 0 or dy != 0:
                    length = math.hypot(dx, dy)
                    self.player.dash_dx = dx / length
                    self.player.dash_dy = dy / length

                    self.player.dash_time = self.player.dash_duration
                    self.player.dash_cooldown = self.player.dash_cd_time

        if key == arcade.key.SPACE:
            self.try_activate_shield()

        # attack handling depends on weapon
        if key in (arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT):
            # if currently axe -> circular AoE around player
            if self.player.weapon == "axe":
                if not self.player.can_attack():
                    return
                self.player.reset_attack()
                # create axe swing
                swing = {"x": self.player.x, "y": self.player.y, "radius": 120, "time": 0.18, "damage": 70, "applied": False}
                self.axe_swings.append(swing)
            # if bow -> spawn projectile arrow in that direction
            elif self.player.weapon == "halberd":
                if not self.player.can_attack():
                    return

                self.player.attack_cooldown = HALBERD_COOLDOWN
                self.player.reset_attack()

                # направление
                if key == arcade.key.UP:
                    angle = 90
                elif key == arcade.key.DOWN:
                    angle = -90
                elif key == arcade.key.LEFT:
                    angle = 180
                else:
                    angle = 0

                swing = {
                    "x": self.player.x,
                    "y": self.player.y,
                    "angle": angle,
                    "radius": HALBERD_RADIUS,
                    "arc": HALBERD_ARC_ANGLE,
                    "time": HALBERD_TIME,
                    "damage": HALBERD_DAMAGE,
                    "applied": False
                }

                self.halberd_swings.append(swing)
                return
            
            if self.player.weapon == "hammer":
                if not self.player.can_attack():
                    return

                self.player.attack_cooldown = HAMMER_COOLDOWN
                self.player.reset_attack()

                if key == arcade.key.UP:
                    angle = 90
                elif key == arcade.key.DOWN:
                    angle = -90
                elif key == arcade.key.LEFT:
                    angle = 180
                else:
                    angle = 0

                swing = {
                    "x": self.player.x,
                "y": self.player.y,
                "radius": HAMMER_RADIUS,
                "timer": HAMMER_WINDUP + HAMMER_IMPACT,
                "phase": "windup",
                "damage": HAMMER_DAMAGE,
                "applied": False
                }   

                self.hammer_swings.append(swing)
                return

            elif self.player.weapon == "bow":
                if not self.player.can_attack():
                    return
                self.player.reset_attack()
                # spawn arrow sprite
                arrow = arcade.Sprite("assets/arrow.png", scale=5)

                arrow.center_x = self.player.x
                arrow.center_y = self.player.y
                # direction vector
                dx = dy = 0
                if key == arcade.key.UP:
                    dy = 1
                elif key == arcade.key.DOWN:
                    dy = -1
                elif key == arcade.key.LEFT:
                    dx = -1
                elif key == arcade.key.RIGHT:
                    dx = 1
                length = math.hypot(dx, dy)
                if length == 0:
                    length = 1
                dx /= length
                dy /= length
                arrow.change_x = dx * ARROW_SPEED
                arrow.change_y = dy * ARROW_SPEED
                arrow.angle = math.degrees(math.atan2(dy, dx))
                arrow.damage = 45
                self.projectile_sprites.append(arrow)
            else:
                # default sword behaviour (directional slash)
                if not self.player.can_attack():
                    return
                self.player.reset_attack()

                x1 = self.player.x
                y1 = self.player.y
                x2 = x1
                y2 = y1
                L = SWORD_LENGTH
                if key == arcade.key.UP:
                    y2 += L
                elif key == arcade.key.DOWN:
                    y2 -= L
                elif key == arcade.key.LEFT:
                    x2 -= L
                elif key == arcade.key.RIGHT:
                    x2 += L

                # visual slash
                self.slashes.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2, "time": SWORD_TIME, "width": SWORD_THICKNESS})

                # damage enemies in area near endpoint
                for e in list(self.current_enemies):
                    if abs(e.x - x2) < 48 and abs(e.y - y2) < 48:
                        e.hp -= 40


        # interact with doors when cleared (or allow entering start room)
        if key == arcade.key.E:
            room = self.floor.get_current_room()
            for door in list(self.door_sprites):
                if arcade.check_for_collision(self.player.sprite, door):
                    target = self.floor.get_current_room().doors.get(door.direction)
                    if not target:
                        continue
                    target_room = self.floor.rooms.get(target)
                    # if target is treasure and locked -> require key
                    if target_room and target_room.type == "treasure" and (not target_room.treasure_unlocked):
                        if self.player.keys > 0:
                            self.player.keys -= 1
                            target_room.treasure_unlocked = True
                            self.notice_text = "Unlocked treasure room!"
                            self.notice_timer = 2.0
                            # move into room
                            if self.floor.move(target):
                                self.load_current_room()
                        else:
                            self.notice_text = "Door is locked. Need a key."
                            self.notice_timer = 2.0
                        break
                    else:
                        # normal move
                        if self.floor.move(target):
                            self.load_current_room()
                        break

        if key == arcade.key.ESCAPE:
            arcade.close_window()

        # debug: R to regenerate floor
        if key == arcade.key.R:
            self.floor = Floor()
            self.current_pos = self.floor.current_pos
            self.load_current_room()

           
    def on_key_release(self, key, modifiers):
        if key in self.keys_held:
            self.keys_held.discard(key)

# ====================== MAIN ======================
def main():
    window = GameWindow()
    arcade.run()

if __name__ == "__main__":
    main()
