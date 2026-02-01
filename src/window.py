import arcade
import random
from src.player import Player
from src.dungeon import Floor
from src.enemy import *
from src.boss import *
from src.settings import *

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
