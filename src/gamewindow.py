import arcade
import random
import math
from maincharac import Player
from enemy import Enemy
from boss import Boss
from pickups import Heart
from settings import SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_TITLE

class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)

        self.attack_hitboxes = []
        self.sword_slashes = []

        self.player = Player()
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player.sprite)

        self.enemy_sprites = arcade.SpriteList()

        self.room_index = 0
        self.rooms = []
        self.current_enemies = []
        self.current_projectiles = []
        self.current_pickups = []
        self.keys_held = set()

        self._create_rooms()
        self._load_room(0)

        self.keys_held = set()

    def _create_rooms(self):
        # создаём 5 комнат. Номер 4 (index=4) — босс
        for i in range(5):
            r = {"enemies": [], "pickups": []}
            if i == 4:
                # босс
                r["enemies"].append(("boss", None))
            else:
                count = 3 + (1 if i >= 2 else 0)
                for _ in range(count):
                    r["enemies"].append(("enemy", None))
                if i in (1, 3):
                    r["pickups"].append(("heart", None))
            self.rooms.append(r)

    def _load_room(self, idx):
        self.room_index = idx
        self.current_enemies.clear()
        self.current_projectiles.clear()
        self.current_pickups.clear()
        # телепорт игрока внизу комнаты
        self.player.sprite.center_x = SCREEN_WIDTH // 2
        self.player.sprite.center_y = 180


        room = self.rooms[idx]
        for etype, _ in room["enemies"]:
            if etype == "boss":
                boss = Boss(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)
                self.current_enemies.append(boss)
                self.enemy_sprites.append(boss.sprite)

            else:
                x = random.randint(200, SCREEN_WIDTH - 200)
                y = random.randint(250, SCREEN_HEIGHT - 200)
                enemy = Enemy(x, y)
                self.current_enemies.append(enemy)
                self.enemy_sprites.append(enemy.sprite)

        for ptype, _ in room["pickups"]:
            if ptype == "heart":
                self.current_pickups.append(Heart(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

        # door state
        self.room_cleared = False
        self.door_open = False

    # ============== Рисование ==============
    def on_draw(self):
        self.clear()
        arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.DARK_SLATE_GRAY)
        self.player_list.draw()
        # сущности
        for heart in self.current_pickups:
            heart.draw()
        for proj in list(self.current_projectiles):
            proj.draw()
        self.enemy_sprites.draw()
        # анимация удара мечом
        for slash in self.sword_slashes:
            arcade.draw_line(
                slash["x1"], slash["y1"],
                slash["x2"], slash["y2"],
                arcade.color.WHITE,
                5
            )

        for hitbox in self.attack_hitboxes:
            arcade.draw_rect_outline(
                hitbox["rect"],
                arcade.color.YELLOW
            )

        # дверь (справа)
        if not self.door_open:
            # рисуем дверной прямоугольник
            left = SCREEN_WIDTH - 160
            bottom = SCREEN_HEIGHT // 2 - 80
            arcade.draw_lbwh_rectangle_filled(left, bottom, 120, 160, arcade.color.DARK_BROWN)
        else:
            arcade.draw_text("Door open → (E)", SCREEN_WIDTH - 420, SCREEN_HEIGHT - 80, arcade.color.LIGHT_GREEN, 28)

        # HUD
        arcade.draw_text(f"HP: {int(self.player.hp)}/{self.player.max_hp}", 20, SCREEN_HEIGHT - 40, arcade.color.WHITE, 28)
        arcade.draw_text(f"Room {self.room_index+1}/5", SCREEN_WIDTH - 260, SCREEN_HEIGHT - 40, arcade.color.WHITE, 24)

        # если босс — показать полосу здоровья
        if any(isinstance(e, Boss) for e in self.current_enemies):
            boss = next(e for e in self.current_enemies if isinstance(e, Boss))
            bar_w = 600
            x = (SCREEN_WIDTH - bar_w) // 2
            y = SCREEN_HEIGHT - 30
            ratio = max(0.0, boss.hp / boss.hp if boss.hp > 0 else 0.0)  # avoid zero division
            # корректный ratio:
            ratio = max(0.0, boss.hp / boss.max_hp)
            arcade.draw_lbwh_rectangle_filled(x, y - 9, int(bar_w * ratio), 18, arcade.color.RED)
            arcade.draw_lrbt_rectangle_outline(x, x + bar_w, y - 9, y + 9, arcade.color.WHITE)

    # ============== Логика обновления ==============
    def on_update(self, dt):
        dx = dy = 0

        if arcade.key.W in self.keys_held:
            dy += 1
        if arcade.key.S in self.keys_held:
            dy -= 1
        if arcade.key.A in self.keys_held:
            dx -= 1
        if arcade.key.D in self.keys_held:
            dx += 1

        if dx or dy:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length

            self.player.sprite.center_x += dx * self.player.speed * dt
            self.player.sprite.center_y += dy * self.player.speed * dt

            if dx > 0:
                self.player.sprite.scale_x = abs(self.player.sprite.scale_x)
            elif dx < 0:
                self.player.sprite.scale_x = -abs(self.player.sprite.scale_x)

            # Ограничение экраном
            self.player.sprite.center_x = max(
                24, min(SCREEN_WIDTH - 24, self.player.sprite.center_x)
            )
            self.player.sprite.center_y = max(
                24, min(SCREEN_HEIGHT - 24, self.player.sprite.center_y)
            )

        self.player.update(dt)

        # обновляем врагов
        for e in list(self.current_enemies):
            if isinstance(e, Boss):
                e.update(self.player, dt, self.current_projectiles)
            else:
                e.update(self.player, dt)

            # простая коллизия с игроком — урон при контакте
            if abs(e.x - self.player.x) < 30 and abs(e.y - self.player.y) < 30:
                self.player.hp -= 30 * dt

            # удаление мертвых
            if e.hp <= 0:
                self.current_enemies.remove(e)
                self.enemy_sprites.remove(e.sprite)


        # пули
        for proj in list(self.current_projectiles):
            proj.update(dt)
            # удаляем если вышли далеко за экран
            if proj.x < -200 or proj.x > SCREEN_WIDTH + 200 or proj.y < -200 or proj.y > SCREEN_HEIGHT + 200:
                if proj in self.current_projectiles:
                    self.current_projectiles.remove(proj)
                continue
            # попал по игроку?
            if abs(proj.x - self.player.x) < 16 and abs(proj.y - self.player.y) < 16:
                self.player.hp -= proj.damage
                if proj in self.current_projectiles:
                    self.current_projectiles.remove(proj)

        # pickups
        for heart in list(self.current_pickups):
            if abs(heart.x - self.player.x) < 30 and abs(heart.y - self.player.y) < 30:
                self.player.max_hp += 20
                self.player.hp = min(self.player.max_hp, self.player.hp + 40)
                self.current_pickups.remove(heart)

        # проверка зачистки
        if not self.current_enemies and not self.room_cleared:
            self.room_cleared = True
            self.door_open = True
            # если pickups есть — они уже размещены и доступны
        
        # обновляем анимацию удара
        for slash in self.sword_slashes[:]:
            slash["time"] -= dt
            if slash["time"] <= 0:
                self.sword_slashes.remove(slash)


        if self.player.hp <= 0:
            self.player = Player()
            self._load_room(self.room_index)
            return



    # ============== Ввод ==============
    def on_key_press(self, key, modifiers):
        self.keys_held.add(key)

        # АТАКА — стрелки
        if key in (arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT):
            if not self.player.can_attack():
                return

            self.player.attack_timer = self.player.attack_cooldown

            # параметры хитбокса
            reach = 68
            half_w = 45
            half_h = 45

            hx = self.player.x
            hy = self.player.y

            if key == arcade.key.UP:
                hy += reach
            elif key == arcade.key.DOWN:
                hy -= reach
            elif key == arcade.key.LEFT:
                hx -= reach
            elif key == arcade.key.RIGHT:
                hx += reach

            # наносим урон всем врагам в зоне удара
            for e in list(self.current_enemies):
                if abs(e.x - hx) < half_w and abs(e.y - hy) < half_h:
                    e.hp -= 30

            # визуальный взмах меча (тонкая линия)
            if key == arcade.key.UP:
                line = (self.player.x - 60, self.player.y + 40,
                        self.player.x + 60, self.player.y + 40)
            elif key == arcade.key.DOWN:
                line = (self.player.x - 60, self.player.y - 40,
                        self.player.x + 60, self.player.y - 40)
            elif key == arcade.key.LEFT:
                line = (self.player.x - 60, self.player.y - 40,
                        self.player.x - 60, self.player.y + 40)
            else:
                line = (self.player.x + 60, self.player.y - 40,
                            self.player.x + 60, self.player.y + 40)

            self.sword_slashes.append({
                "x1": line[0],
                "y1": line[1],
                "x2": line[2],
                "y2": line[3],
                "time": 0.12
            })


        # дверь
        if key == arcade.key.E and self.door_open:
            next_idx = self.room_index + 1
            if next_idx < len(self.rooms):
                self._load_room(next_idx)
            else:
                self._load_room(0)

        if key == arcade.key.ESCAPE:
            arcade.close_window()


    def try_attack(self, direction):
        if not self.player.attack_timer <= 0:
            return
        self.player.attack_timer = self.player.attack_cooldown

    def on_key_release(self, key, modifiers):
        self.keys_held.discard(key)