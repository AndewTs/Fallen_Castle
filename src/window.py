# window.py
import arcade
import math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, SWORD_LENGTH, SWORD_THICKNESS, SWORD_TIME
from player import Player
from enemy import Enemy
from boss import Boss
from dungeon import Floor

# helper for wall tile size
WALL_TILE = 64

class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        # player and spritelists
        self.player = Player(SCREEN_WIDTH // 2, 120)
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player.sprite)

        self.enemy_sprites = arcade.SpriteList()
        self.wall_sprites = arcade.SpriteList()

        # floor / rooms
        self.floor = Floor()
        self.current_pos = self.floor.current_pos

        # runtime entity objects for the current room
        self.current_enemies = []  # list of Enemy/Boss instances

        # attack visuals
        self.slashes = []  # dicts with x1,y1,x2,y2,time,width

        self.door_sprites = arcade.SpriteList()

        # input
        self.keys_held = set()

        # room state
        self.room_cleared = False

        # load first room
        self.load_current_room()

    # ----------------------
    # room loading / spawn
    # ----------------------
    def load_current_room(self):
        # clear previous
        self.enemy_sprites.clear()
        self.wall_sprites.clear()
        self.current_enemies.clear()
        self.slashes.clear()
        self.room_cleared = False

        room = self.floor.get_current_room()

        room.forbidden_zones.clear()

# старт игрока
        room.add_forbidden_zone(SCREEN_WIDTH // 2, 190, 120)

# двери
        for direction in room.doors:
            if direction == "up":
                room.add_forbidden_zone(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80, 140)
            elif direction == "down":
                room.add_forbidden_zone(SCREEN_WIDTH // 2, 80, 140)
            elif direction == "left":
                room.add_forbidden_zone(80, SCREEN_HEIGHT // 2, 140)
            elif direction == "right":
                room.add_forbidden_zone(SCREEN_WIDTH - 80, SCREEN_HEIGHT // 2, 140)


        # spawn walls: border + some rocks
        # top/bottom rows
        for x in range(0, SCREEN_WIDTH, WALL_TILE):
            # bottom
            rock = arcade.SpriteSolidColor(WALL_TILE, WALL_TILE, arcade.color.DARK_BROWN)
            rock.center_x = x + WALL_TILE // 2
            rock.center_y = WALL_TILE // 2
            self.wall_sprites.append(rock)
            # top
            rock2 = arcade.SpriteSolidColor(WALL_TILE, WALL_TILE, arcade.color.DARK_BROWN)
            rock2.center_x = x + WALL_TILE // 2
            rock2.center_y = SCREEN_HEIGHT - WALL_TILE // 2
            self.wall_sprites.append(rock2)
        # left/right
        for y in range(WALL_TILE, SCREEN_HEIGHT - WALL_TILE, WALL_TILE):
            rock = arcade.SpriteSolidColor(WALL_TILE, WALL_TILE, arcade.color.DARK_BROWN)
            rock.center_x = WALL_TILE // 2
            rock.center_y = y + WALL_TILE // 2
            self.wall_sprites.append(rock)
            rock2 = arcade.SpriteSolidColor(WALL_TILE, WALL_TILE, arcade.color.DARK_BROWN)
            rock2.center_x = SCREEN_WIDTH - WALL_TILE // 2
            rock2.center_y = y + WALL_TILE // 2
            self.wall_sprites.append(rock2)

        # spawn obstacles inside room (a few rocks)
        import random
        def is_position_allowed(x, y, forbidden):
            for fx, fy, r in forbidden:
                if abs(x - fx) < r and abs(y - fy) < r:
                    return False
            return True

        room = self.floor.get_current_room()
        attempts = 0
        spawned = 0
        if room.type != 'boss' and room.type != 'start':
            while spawned < 6 and attempts < 100:
                attempts += 1
                x = random.randint(180, SCREEN_WIDTH - 180)
                y = random.randint(180, SCREEN_HEIGHT - 180)

                if not is_position_allowed(x, y, room.forbidden_zones):
                    continue

                rock = arcade.Sprite("assets/rock.png", scale=6.0)
                rock.center_x = x
                rock.center_y = y
                self.wall_sprites.append(rock)
                spawned += 1

        # spawn enemies from room.enemy_spawns
        # boss room? spawn boss
        if room.type == "boss":
            boss = Boss(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
            self.current_enemies.append(boss)
            self.enemy_sprites.append(boss.sprite)
        else:
            for spawn in room.enemy_spawns:
                x, y = self.find_free_position()
                e = Enemy(x, y)
                self.current_enemies.append(e)
                self.enemy_sprites.append(e.sprite)
        
        self.room_cleared = len(self.current_enemies) == 0

        # teleport player to entrance side if coming from another room: keep center for simplicity
        self.player.sprite.center_x = SCREEN_WIDTH // 2
        self.player.sprite.center_y = 190

        self.door_sprites.clear()

        margin = 80

        def spawn_door(x, y, direction):
            door = arcade.Sprite("assets/door.png", scale=6.0)
            door.center_x = x
            door.center_y = y
            door.direction = direction
            self.door_sprites.append(door)

        room = self.floor.get_current_room()

        if room.doors.get("up") is not None:
            spawn_door(SCREEN_WIDTH // 2, SCREEN_HEIGHT - margin, "up")

        if room.doors.get("down") is not None:
            spawn_door(SCREEN_WIDTH // 2, margin, "down")

        if room.doors.get("left") is not None:
            spawn_door(margin, SCREEN_HEIGHT // 2, "left")

        if room.doors.get("right") is not None:
            spawn_door(SCREEN_WIDTH - margin, SCREEN_HEIGHT // 2, "right")


    # ----------------------
    # drawing
    # ----------------------
    def on_draw(self):
        self.clear()

        # floor background
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.DARK_SLATE_GRAY)

        # walls, enemies, player
        self.wall_sprites.draw()
        self.enemy_sprites.draw()
        self.player_list.draw()
        self.door_sprites.draw()

        # draw slashes
        for s in self.slashes:
            arcade.draw_line(s["x1"], s["y1"], s["x2"], s["y2"], arcade.color.WHITE, s["width"])

        # HUD
        arcade.draw_text(f"HP: {int(self.player.hp)}/{self.player.max_hp}", 12, SCREEN_HEIGHT - 28, arcade.color.BLACK, 18)
        arcade.draw_text(f"Room: {self.floor.current_pos}", 12, SCREEN_HEIGHT - 54, arcade.color.LIGHT_GRAY, 14)

        # doors drawn as rectangles; green when cleared
        room = self.floor.get_current_room()
        door_color = arcade.color.LIGHT_GREEN if self.room_cleared else arcade.color.DARK_BROWN
        w, h = 120, 160

        if self.room_cleared:
            arcade.draw_text("Press E near a door to enter", SCREEN_WIDTH//2 - 160, 24, arcade.color.WHITE, 14)

    # ----------------------
    # update
    # ----------------------
    def on_update(self, dt):
        # movement - read keys
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

        # update enemies
        for e in list(self.current_enemies):
            if isinstance(e, Boss):
                e.update_phase(self.player, self.wall_sprites, dt)
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

        # project slashes lifetime
        for s in list(self.slashes):
            s["time"] -= dt
            if s["time"] <= 0:
                self.slashes.remove(s)

        # room cleared?
        self.room_cleared = len(self.current_enemies) == 0

        if self.player.hp <= 0:
            # пересоздаём этаж
            self.floor = Floor()
            self.current_pos = self.floor.current_pos

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

        # attack: arrows
        if key in (arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT):
            if not self.player.can_attack():
                return
            self.player.reset_attack()

            # compute slash endpoints
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

        # interact with doors when cleared
        if key == arcade.key.E and (self.room_cleared or self.floor.get_current_room().type == "start"):
            room = self.floor.get_current_room()
            for door in self.door_sprites:
                if arcade.check_for_collision(self.player.sprite, door):
                    target = self.floor.get_current_room().doors.get(door.direction)
                    if target and self.floor.move(target):
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

    # ----------------------
    # helper: near door
    # ----------------------
    def player_near_door(self, direction):
        px = self.player.x
        py = self.player.y
        margin = 180
        if direction == "up":
            return py > SCREEN_HEIGHT - margin
        if direction == "down":
            return py < margin
        if direction == "left":
            return px < margin
        if direction == "right":
            return px > SCREEN_WIDTH - margin
        return False
    
    def find_free_position(self, min_x=150, max_x=None, min_y=150, max_y=None, tries=100):
        import random

        if max_x is None:
            max_x = SCREEN_WIDTH - 150
        if max_y is None:
            max_y = SCREEN_HEIGHT - 150

        for _ in range(tries):
            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)

            dummy = arcade.SpriteSolidColor(32, 32, arcade.color.RED)
            dummy.center_x = x
            dummy.center_y = y

            if not arcade.check_for_collision_with_list(dummy, self.wall_sprites):
                return x, y

        return SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

