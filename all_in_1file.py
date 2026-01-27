import arcade
import time
import random
import math
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum

# ============== ИЗМЕНЕНО: ОБЩИЕ КОНСТАНТЫ ==============
# Используем разрешение для окна 1024x768
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Fallen Castle"

PIXEL = 4  # Уменьшен размер пикселя для отрисовки (чтобы лучше вписывалось)

BOSS_MATRIX = [
    "001111100",
    "011111110",
    "1110110111",
    "1111111111",
    "1111111111",
    "011111110",
    "001111100",
]

HEART_MATRIX = [
    "0100010",
    "1110111",
    "1111111",
    "0111110",
    "0011100",
    "0001000",
]

# Цвета для меню
BUTTON_NORMAL = (87, 76, 41)
BUTTON_HOVER = (128, 112, 61)
BUTTON_PRESSED = (107, 92, 44)
TEXT_COLOR = (255, 255, 255, 255)
BUTTON_BORDER = (130, 114, 62)
UI_BACKGROUND = (40, 40, 40, 200)

# Размеры тайлов для стен и препятствий
WALL_TILE = 48  # Уменьшено для меньшего окна
OBSTACLE_SCALE = 4.0  # Уменьшено

# Типы комнат
class RoomType(Enum):
    START = "start"
    NORMAL = "normal"
    BOSS = "boss"

# ============== Утилита отрисовки пикселей ==============
def draw_pixel_matrix(matrix, x, y, color):
    for r, row in enumerate(matrix):
        for c, cell in enumerate(row):
            if cell == "1":
                left = x + c * PIXEL
                bottom = y - (r + 1) * PIXEL
                arcade.draw_lbwh_rectangle_filled(left, bottom, PIXEL, PIXEL, color)

# ============== КЛАСС КОМНАТЫ ==============
class Room:
    def __init__(self, pos, room_type="normal"):
        self.pos = pos
        self.type = room_type
        self.doors = {}  # направление: (x, y) позиция в сетке
        self.enemy_spawns = []
        self.forbidden_zones = []
        
        if self.type == RoomType.START:
            enemy_count = 0
        elif self.type == RoomType.BOSS:
            enemy_count = 0  # Босс будет добавлен отдельно
        else:
            enemy_count = random.randint(2, 4)  # Уменьшено количество врагов
        
        for _ in range(enemy_count):
            self.enemy_spawns.append({"type": "enemy", "x": None, "y": None, "hp": None})
    
    def set_doors(self, doors_dict):
        self.doors = doors_dict
    
    def add_forbidden_zone(self, x, y, radius):
        self.forbidden_zones.append((x, y, radius))

# ============== КЛАСС ЭТАЖА ==============
class Floor:
    def __init__(self, floor_number, size=3):
        self.floor_number = floor_number
        self.size = size
        self.rooms = {}
        self.start_pos = (0, 0)
        self.boss_pos = (size - 1, size - 1)
        self.current_pos = self.start_pos
        self.generate()
    
    def generate(self):
        # Создаем комнаты
        for x in range(self.size):
            for y in range(self.size):
                pos = (x, y)
                if pos == self.start_pos:
                    room_type = RoomType.START
                elif pos == self.boss_pos:
                    room_type = RoomType.BOSS
                else:
                    room_type = RoomType.NORMAL
                
                room = Room(pos, room_type)
                self.rooms[pos] = room
        
        # Создаем связи между комнатами (двери)
        directions = {
            "up": (0, 1),
            "down": (0, -1),
            "left": (-1, 0),
            "right": (1, 0)
        }
        
        for (x, y), room in self.rooms.items():
            doors = {}
            for name, (dx, dy) in directions.items():
                npos = (x + dx, y + dy)
                if npos in self.rooms:
                    doors[name] = npos
            room.set_doors(doors)
            
            # Добавляем запретные зоны вокруг дверей
            DOOR_MARGIN = 100  # Уменьшено
            if "up" in doors:
                room.add_forbidden_zone(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60, DOOR_MARGIN)
            if "down" in doors:
                room.add_forbidden_zone(SCREEN_WIDTH // 2, 60, DOOR_MARGIN)
            if "left" in doors:
                room.add_forbidden_zone(60, SCREEN_HEIGHT // 2, DOOR_MARGIN)
            if "right" in doors:
                room.add_forbidden_zone(SCREEN_WIDTH - 60, SCREEN_HEIGHT // 2, DOOR_MARGIN)
            
            # Стартовая позиция игрока
            if room.type == RoomType.START:
                room.add_forbidden_zone(SCREEN_WIDTH // 2, 140, 150)  # Уменьшено
    
    def get_current_room(self):
        return self.rooms[self.current_pos]
    
    def move(self, direction):
        current_room = self.get_current_room()
        if direction in current_room.doors:
            self.current_pos = current_room.doors[direction]
            return True
        return False

# ============== ОКНО СЮЖЕТА ==============
class StoryView(arcade.View):
    def __init__(self, previous_view):
        super().__init__()
        self.previous_view = previous_view
        self.button_list = []
        self.hovered_button = None
        self.pressed_button = None
        self.current_page = 0
        self.pages = [
            {
                "title": "ПРОЛОГ",
                "content": [
                    "Пробудившись ото сна длиною в тысячелетие,",
                    "отважный рыцарь обнаружил себя",
                    "в древних стенах забытого замка.",
                    "Память была пуста, и лишь зовущее эхо прошлого",
                    "вело его сквозь сумрак коридоров,",
                    "чтобы восстановить нить событий."
                ]
            },
            {
                "title": "ГЛАВА 1: КРЕПОСТНАЯ СТЕНА",
                "content": [
                    "Первый этаж, крепостная стена.",
                    "Здесь рыцарь встречает первых врагов.",
                    "Он должен пройти через все комнаты,",
                    "чтобы найти путь в цитадель."
                ]
            },
            {
                "title": "ГЛАВА 2: ЦИТАДЕЛЬ",
                "content": [
                    "Второй этаж, цитадель.",
                    "Здесь враги становятся сильнее,",
                    "а комнаты - больше.",
                    "Рыцарь должен быть осторожен."
                ]
            },
            {
                "title": "ГЛАВА 3: ПОДЗЕМЕЛЬЕ",
                "content": [
                    "Третий этаж, подземелье.",
                    "Самое опасное место в замке.",
                    "Здесь обитает могущественный босс,",
                    "которого нужно победить, чтобы завершить историю."
                ]
            }
        ]
        
    def setup(self):
        # Кнопка "НАЗАД"
        back_button = {
            "x": 30,
            "y": 30,
            "width": 150,
            "height": 40,
            "text": "НАЗАД",
            "action": "back"
        }
        self.button_list.append(back_button)
        
        # Кнопка "ПРЕДЫДУЩАЯ"
        prev_button = {
            "x": SCREEN_WIDTH // 2 - 180,
            "y": 80,
            "width": 160,
            "height": 40,
            "text": "ПРЕДЫДУЩАЯ",
            "action": "prev"
        }
        self.button_list.append(prev_button)
        
        # Кнопка "СЛЕДУЮЩАЯ"
        next_button = {
            "x": SCREEN_WIDTH // 2 + 20,
            "y": 80,
            "width": 160,
            "height": 40,
            "text": "СЛЕДУЮЩАЯ",
            "action": "next"
        }
        self.button_list.append(next_button)
        
    def on_draw(self):
        self.clear()
        
        # Фон на весь экран
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                SCREEN_WIDTH // 2, 
                SCREEN_HEIGHT // 2, 
                SCREEN_WIDTH, 
                SCREEN_HEIGHT
            ),
            (20, 20, 40)
        )
        
        # Текущая страница
        page = self.pages[self.current_page]
        
        # Заголовок
        arcade.draw_text(
            page["title"], 
            SCREEN_WIDTH // 2, 
            SCREEN_HEIGHT - 70,
            (255, 215, 0),
            36,
            anchor_x="center",
            anchor_y="center",
            font_name=("Arial", "arial"),
            bold=True
        )
        
        # Содержание
        y_pos = SCREEN_HEIGHT - 140
        for line in page["content"]:
            arcade.draw_text(
                line,
                SCREEN_WIDTH // 2,
                y_pos,
                (220, 220, 220),
                24,
                anchor_x="center",
                anchor_y="center",
                font_name=("Arial", "arial")
            )
            y_pos -= 35
        
        # Номер страницы
        arcade.draw_text(
            f"Страница {self.current_page + 1} из {len(self.pages)}",
            SCREEN_WIDTH // 2,
            150,
            (200, 200, 200),
            22,
            anchor_x="center",
            anchor_y="center",
            font_name=("Arial", "arial")
        )
        
        # Отрисовка кнопок
        for button in self.button_list:
            # Определяем цвет кнопки
            if self.pressed_button == button:
                color = BUTTON_PRESSED
            elif self.hovered_button == button:
                color = BUTTON_HOVER
            else:
                color = BUTTON_NORMAL
            
            # Рисуем кнопку
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    button["x"] + button["width"] // 2,
                    button["y"] + button["height"] // 2,
                    button["width"],
                    button["height"]
                ),
                color
            )
            
            # Рамка кнопки
            arcade.draw_rect_outline(
                arcade.rect.XYWH(
                    button["x"] + button["width"] // 2,
                    button["y"] + button["height"] // 2,
                    button["width"],
                    button["height"]
                ),
                BUTTON_BORDER,
                2
            )
            
            # Текст кнопки
            arcade.draw_text(
                button["text"],
                button["x"] + button["width"] // 2,
                button["y"] + button["height"] // 2,
                TEXT_COLOR,
                18,
                anchor_x="center",
                anchor_y="center",
                font_name=("Arial", "arial"),
                bold=True
            )
    
    def on_mouse_motion(self, x, y, dx, dy):
        self.hovered_button = None
        for button in self.button_list:
            if (button["x"] <= x <= button["x"] + button["width"] and 
                button["y"] <= y <= button["y"] + button["height"]):
                self.hovered_button = button
                break
    
    def on_mouse_press(self, x, y, button, modifiers):
        self.pressed_button = None
        for btn in self.button_list:
            if (btn["x"] <= x <= btn["x"] + btn["width"] and 
                btn["y"] <= y <= btn["y"] + btn["height"]):
                self.pressed_button = btn
                break
    
    def on_mouse_release(self, x, y, button, modifiers):
        if self.pressed_button:
            for btn in self.button_list:
                if (btn["x"] <= x <= btn["x"] + btn["width"] and 
                    btn["y"] <= y <= btn["y"] + btn["height"] and 
                    btn == self.pressed_button):
                    
                    if btn["action"] == "back":
                        # Возвращаемся к предыдущему экрану
                        self.window.show_view(self.previous_view)
                    
                    elif btn["action"] == "prev":
                        if self.current_page > 0:
                            self.current_page -= 1
                    
                    elif btn["action"] == "next":
                        if self.current_page < len(self.pages) - 1:
                            self.current_page += 1
                    
                    break
        
        self.pressed_button = None
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            # Возврат к предыдущему экрану
            self.window.show_view(self.previous_view)
        elif key == arcade.key.LEFT:
            if self.current_page > 0:
                self.current_page -= 1
        elif key == arcade.key.RIGHT:
            if self.current_page < len(self.pages) - 1:
                self.current_page += 1

# ============== ИНТРО-ЭКРАН ДЛЯ ПЕРВОГО УРОВНЯ ==============
class IntroView(arcade.View):
    def __init__(self, floor_number):
        super().__init__()
        self.floor_number = floor_number
        self.button_list = []
        self.hovered_button = None
        self.pressed_button = None
        
    def setup(self):
        # Создаем кнопку "ПРОДОЛЖИТЬ"
        continue_button = {
            "x": SCREEN_WIDTH // 2 - 120,
            "y": 80,
            "width": 240,
            "height": 50,
            "text": "ПРОДОЛЖИТЬ",
            "action": "continue"
        }
        self.button_list.append(continue_button)
        
    def on_draw(self):
        self.clear()
        
        # Черный фон на весь экран
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                SCREEN_WIDTH // 2, 
                SCREEN_HEIGHT // 2, 
                SCREEN_WIDTH, 
                SCREEN_HEIGHT
            ),
            (0, 0, 0)
        )
        
        # Текст интро (разделенный на строки)
        intro_text_lines = [
            "Пробудившись ото сна длиною в тысячелетие,",
            "отважный рыцарь обнаружил себя",
            "в древних стенах забытого замка.",
            "Память была пуста, и лишь зовущее эхо прошлого",
            "вело его сквозь сумрак коридоров,",
            "чтобы восстановить нить событий."
        ]
        
        # Рисуем текст интро по центру экрана
        y_pos = SCREEN_HEIGHT // 2 + 60
        for i, line in enumerate(intro_text_lines):
            arcade.draw_text(
                line,
                SCREEN_WIDTH // 2,
                y_pos - i * 30,
                (255, 255, 255),
                20,
                anchor_x="center",
                anchor_y="center",
                font_name=("Arial", "arial"),
                bold=(i == 0)
            )
        
        # Отрисовка кнопки "ПРОДОЛЖИТЬ"
        for button in self.button_list:
            # Определяем цвет кнопки
            if self.pressed_button == button:
                color = BUTTON_PRESSED
            elif self.hovered_button == button:
                color = BUTTON_HOVER
            else:
                color = BUTTON_NORMAL
            
            # Рисуем кнопку
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    button["x"] + button["width"] // 2,
                    button["y"] + button["height"] // 2,
                    button["width"],
                    button["height"]
                ),
                color
            )
            
            # Рамка кнопки
            arcade.draw_rect_outline(
                arcade.rect.XYWH(
                    button["x"] + button["width"] // 2,
                    button["y"] + button["height"] // 2,
                    button["width"],
                    button["height"]
                ),
                BUTTON_BORDER,
                2
            )
            
            # Текст кнопки
            arcade.draw_text(
                button["text"],
                button["x"] + button["width"] // 2,
                button["y"] + button["height"] // 2,
                TEXT_COLOR,
                20,
                anchor_x="center",
                anchor_y="center",
                font_name=("Arial", "arial"),
                bold=True
            )
    
    def on_mouse_motion(self, x, y, dx, dy):
        self.hovered_button = None
        for button in self.button_list:
            if (button["x"] <= x <= button["x"] + button["width"] and 
                button["y"] <= y <= button["y"] + button["height"]):
                self.hovered_button = button
                break
    
    def on_mouse_press(self, x, y, button, modifiers):
        self.pressed_button = None
        for btn in self.button_list:
            if (btn["x"] <= x <= btn["x"] + btn["width"] and 
                btn["y"] <= y <= btn["y"] + btn["height"]):
                self.pressed_button = btn
                break
    
    def on_mouse_release(self, x, y, button, modifiers):
        if self.pressed_button:
            for btn in self.button_list:
                if (btn["x"] <= x <= btn["x"] + btn["width"] and 
                    btn["y"] <= y <= btn["y"] + btn["height"] and 
                    btn == self.pressed_button):
                    
                    if btn["action"] == "continue":
                        # Переходим к игровому уровню
                        game_view = GameView()
                        game_view.setup(self.floor_number)
                        self.window.show_view(game_view)
                    
                    break
        
        self.pressed_button = None
    
    def on_key_press(self, key, modifiers):
        # Разрешаем нажатие Enter для продолжения
        if key == arcade.key.ENTER or key == arcade.key.SPACE:
            game_view = GameView()
            game_view.setup(self.floor_number)
            self.window.show_view(game_view)
        elif key == arcade.key.ESCAPE:
            # Возврат к выбору этажа
            floor_view = FloorSelectionView()
            floor_view.setup()
            self.window.show_view(floor_view)


# ============== СУЩНОСТИ ИГРЫ ==============
class Player:
    def __init__(self):
        try:
            self.sprite = arcade.Sprite("assets/sprites/Player 2.png", scale=0.08)  # Уменьшен масштаб
        except:
            # Заглушка если файл не найден
            self.sprite = arcade.SpriteSolidColor(40, 40, arcade.color.BLUE)
        
        self.sprite.center_x = SCREEN_WIDTH // 2
        self.sprite.center_y = SCREEN_HEIGHT // 2

        self.speed = 200  # Уменьшена скорость
        self.hp = 100
        self.max_hp = 100

        self.attack_cooldown = 0.25
        self.attack_timer = 0.0

        self.attack_dir = None

    @property
    def x(self):
        return self.sprite.center_x

    @property
    def y(self):
        return self.sprite.center_y

    def move(self, dx, dy):
        self.sprite.center_x += dx
        self.sprite.center_y += dy

        # ограничение по экрану
        self.sprite.center_x = max(20, min(SCREEN_WIDTH - 20, self.sprite.center_x))
        self.sprite.center_y = max(20, min(SCREEN_HEIGHT - 20, self.sprite.center_y))

    def update(self, dt):
        if self.attack_timer > 0:
            self.attack_timer -= dt

    def can_attack(self):
        return self.attack_timer <= 0

    def reset_attack(self):
        self.attack_timer = self.attack_cooldown


class Enemy:
    def __init__(self, x, y):
        try:
            self.sprite = arcade.Sprite("assets/sprites/enemy.png", scale=0.07)  # Уменьшен масштаб
        except:
            # Заглушка если файл не найден
            self.sprite = arcade.SpriteSolidColor(32, 32, arcade.color.RED)
        
        self.sprite.center_x = x
        self.sprite.center_y = y

        self.hp = 60
        self.speed = 160  # Уменьшена скорость

    # удобные прокси
    @property
    def x(self):
        return self.sprite.center_x

    @property
    def y(self):
        return self.sprite.center_y

    def update(self, player, dt, walls):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist < 200 and dist > 1:  # Уменьшена дистанция преследования
            vx = dx / dist * self.speed * dt
            vy = dy / dist * self.speed * dt

            # Движение с проверкой столкновений
            old_x = self.sprite.center_x
            self.sprite.center_x += vx
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_x = old_x

            old_y = self.sprite.center_y
            self.sprite.center_y += vy
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_y = old_y

            # Поворот спрайта
            if dx > 0:
                self.sprite.scale_x = -abs(self.sprite.scale_x)
            else:
                self.sprite.scale_x = +abs(self.sprite.scale_x)


class Boss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        try:
            self.sprite.texture = arcade.load_texture("assets/sprites/boss.png")
        except:
            pass  # Оставляем заглушку если текстура не найдена
        
        self.sprite.scale = 0.075  # Уменьшен масштаб
        self.max_hp = 120
        self.hp = self.max_hp
        self.phase = 1
        self.shoot_timer = 2.0
        self.dash_timer = 5.0

    def update(self, player, dt, projectiles, walls):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        
        # Движение с проверкой столкновений
        if dist > 120:  # Уменьшена дистанция
            vx = (dx / dist) * (70 + 15 * self.phase) * dt  # Уменьшена скорость
            vy = (dy / dist) * (70 + 15 * self.phase) * dt
            
            old_x = self.sprite.center_x
            self.sprite.center_x += vx
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_x = old_x

            old_y = self.sprite.center_y
            self.sprite.center_y += vy
            if arcade.check_for_collision_with_list(self.sprite, walls):
                self.sprite.center_y = old_y

        # Фазы
        if self.hp < 200:
            self.phase = 2
        if self.hp < 100:
            self.phase = 3

        # Стрельба
        self.shoot_timer -= dt
        if self.shoot_timer <= 0:
            self.shoot_timer = max(0.6, 2.0 - 0.4 * self.phase)
            offsets = (-0.3, 0.0, 0.3) if self.phase == 1 else (-0.5, -0.2, 0.0, 0.2, 0.5)
            for off in offsets:
                projectiles.append(Projectile(self.x, self.y, player.x, player.y, 
                                            angle_offset=off, speed=350 + 30*self.phase,  # Уменьшена скорость
                                            damage=10 + 4*self.phase))

        # Рывок
        self.dash_timer -= dt
        if self.dash_timer <= 0:
            self.dash_timer = max(2.0, 5.0 - self.phase)
            if dist > 10:
                nx = dx / dist
                ny = dy / dist
                dash_dist = 180 + 30 * self.phase  # Уменьшена дистанция рывка
                
                # Рывок с проверкой столкновений
                old_x = self.sprite.center_x
                old_y = self.sprite.center_y
                self.sprite.center_x += nx * dash_dist
                self.sprite.center_y += ny * dash_dist
                
                if arcade.check_for_collision_with_list(self.sprite, walls):
                    self.sprite.center_x = old_x
                    self.sprite.center_y = old_y


class Projectile:
    def __init__(self, x, y, tx, ty, angle_offset=0.0, speed=350.0, damage=8):  # Уменьшена скорость
        self.x = x
        self.y = y
        dx = tx - x
        dy = ty - y
        base = math.atan2(dy, dx)
        angle = base + angle_offset
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.damage = damage

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self):
        left = self.x - 3  # Уменьшен размер
        bottom = self.y - 3
        arcade.draw_lbwh_rectangle_filled(left, bottom, 6, 6, arcade.color.YELLOW)


class Heart:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        matrix_w = len(HEART_MATRIX[0]) * PIXEL
        matrix_h = len(HEART_MATRIX) * PIXEL
        top_left_x = self.x - matrix_w // 2
        top_left_y = self.y + matrix_h // 2
        draw_pixel_matrix(HEART_MATRIX, top_left_x, top_left_y, arcade.color.PINK)


# ============== КЛАССЫ ДЛЯ МЕНЮ ==============
class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    PASSIVE = "passive"
    ACTIVE = "active"
    RESOURCE = "resource"


@dataclass
class Item:
    name: str
    item_type: ItemType
    description: str
    stats: Optional[Dict] = None
    color: Optional[Tuple[int, int, int]] = None
    
    def __post_init__(self):
        if self.stats is None:
            self.stats = {}
        if self.color is None:
            self.color = self.get_default_color()
    
    def get_default_color(self):
        colors = {
            ItemType.WEAPON: (192, 192, 192),
            ItemType.ARMOR: (184, 134, 11),
            ItemType.PASSIVE: (138, 43, 226),
            ItemType.ACTIVE: (0, 191, 255),
            ItemType.RESOURCE: (50, 205, 50)
        }
        return colors.get(self.item_type, (255, 255, 255))


# ============== ОБУЧЕНИЕ ==============
class TutorialView(arcade.View):
    def __init__(self, previous_view):
        super().__init__()
        self.previous_view = previous_view
        self.button_list = []
        self.hovered_button = None
        self.pressed_button = None
        
    def setup(self):
        # Кнопка возврата
        back_button = {
            "x": SCREEN_WIDTH // 2 - 80,
            "y": 40,
            "width": 160,
            "height": 40,
            "text": "НАЗАД",
            "action": "back"
        }
        self.button_list.append(back_button)
        
    def on_draw(self):
        self.clear()
        
        # Фон на весь экран
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                SCREEN_WIDTH // 2, 
                SCREEN_HEIGHT // 2, 
                SCREEN_WIDTH, 
                SCREEN_HEIGHT
            ),
            (20, 20, 40)
        )
        
        # Заголовок
        arcade.draw_text(
            "ОБУЧЕНИЕ", 
            SCREEN_WIDTH // 2, 
            SCREEN_HEIGHT - 60,
            (255, 215, 0),
            36,
            anchor_x="center",
            anchor_y="center",
            font_name=("Arial", "arial"),
            bold=True
        )
        
        # Текст обучения
        tutorial_text = [
            "УПРАВЛЕНИЕ:",
            "W, A, S, D - движение",
            "Стрелки - атака в направлении",
            "E - войти в дверь",
            "ESC - выход в меню",
            "",
            "ЦЕЛЬ ИГРЫ:",
            "Исследуйте все комнаты этажа",
            "В последней комнате сразитесь с боссом",
            "",
            "",
            "ПОДСКАЗКИ:",
            "• Красные сердца увеличивают максимальное здоровье",
            "• Используйте коробки для укрытия от врагов",
            "• Уклоняйтесь от снарядов босса",
            "• Двери откроются после уничтожения всех врагов",
            "• Исследуйте все комнаты для нахождения секретов"
        ]
        
        y_pos = SCREEN_HEIGHT - 100
        for line in tutorial_text:
            if line.startswith("•"):
                color = (200, 200, 100)
                font_size = 16
            elif line.endswith(":"):
                color = (255, 215, 0)
                font_size = 20
            else:
                color = (220, 220, 220)
                font_size = 18
            
            if line:  # Не рисуем пустые строки
                arcade.draw_text(
                    line,
                    SCREEN_WIDTH // 2,
                    y_pos,
                    color,
                    font_size,
                    anchor_x="center",
                    anchor_y="center",
                    font_name=("Arial", "arial"),
                    bold=(line.endswith(":"))
                )
            y_pos -= 25
        
        # Отрисовка кнопок
        for button in self.button_list:
            # Определяем цвет кнопки
            if self.pressed_button == button:
                color = BUTTON_PRESSED
            elif self.hovered_button == button:
                color = BUTTON_HOVER
            else:
                color = BUTTON_NORMAL
            
            # Рисуем кнопку
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    button["x"] + button["width"] // 2,
                    button["y"] + button["height"] // 2,
                    button["width"],
                    button["height"]
                ),
                color
            )
            
            # Рамка кнопки
            arcade.draw_rect_outline(
                arcade.rect.XYWH(
                    button["x"] + button["width"] // 2,
                    button["y"] + button["height"] // 2,
                    button["width"],
                    button["height"]
                ),
                BUTTON_BORDER,
                2
            )
            
            # Текст кнопки
            arcade.draw_text(
                button["text"],
                button["x"] + button["width"] // 2,
                button["y"] + button["height"] // 2,
                TEXT_COLOR,
                18,
                anchor_x="center",
                anchor_y="center",
                font_name=("Arial", "arial"),
                bold=True
            )
    
    def on_mouse_motion(self, x, y, dx, dy):
        self.hovered_button = None
        for button in self.button_list:
            if (button["x"] <= x <= button["x"] + button["width"] and 
                button["y"] <= y <= button["y"] + button["height"]):
                self.hovered_button = button
                break
    
    def on_mouse_press(self, x, y, button, modifiers):
        self.pressed_button = None
        for btn in self.button_list:
            if (btn["x"] <= x <= btn["x"] + btn["width"] and 
                btn["y"] <= y <= btn["y"] + btn["height"]):
                self.pressed_button = btn
                break
    
    def on_mouse_release(self, x, y, button, modifiers):
        if self.pressed_button:
            for btn in self.button_list:
                if (btn["x"] <= x <= btn["x"] + btn["width"] and 
                    btn["y"] <= y <= btn["y"] + btn["height"] and 
                    btn == self.pressed_button):
                    
                    if btn["action"] == "back":
                        # Возвращаемся к предыдущему экрану
                        self.window.show_view(self.previous_view)
                    
                    break
        
        self.pressed_button = None
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            # Возврат к предыдущему экрану
            self.window.show_view(self.previous_view)


# ============== ГЛАВНОЕ МЕНЮ ==============
class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.button_list = []
        self.hovered_button = None
        self.pressed_button = None
        
    def setup(self):
        # Загрузка фона
        try:
            self.background_texture = arcade.load_texture("data/images/Main_Background.png")
        except:
            self.background_texture = None
        
        # Создаем кнопки
        button_width = 320
        button_height = 50
        
        # Кнопка "Начать игру"
        start_button = {
            "x": SCREEN_WIDTH // 2 - button_width // 2,
            "y": SCREEN_HEIGHT // 2 - 30,
            "width": button_width,
            "height": button_height,
            "text": "НАЧАТЬ ИГРУ",
            "action": "start"
        }
        self.button_list.append(start_button)
        
        # Кнопка "Выход"
        exit_button = {
            "x": SCREEN_WIDTH // 2 - button_width // 2,
            "y": SCREEN_HEIGHT // 2 - 90,
            "width": button_width,
            "height": button_height,
            "text": "ВЫХОД",
            "action": "exit"
        }
        self.button_list.append(exit_button)
        
    def on_draw(self):
        self.clear()
        
        # Отрисовка фона на весь экран
        if self.background_texture:
            arcade.draw_texture_rect(
                self.background_texture,
                arcade.rect.XYWH(
                    SCREEN_WIDTH // 2, 
                    SCREEN_HEIGHT // 2, 
                    SCREEN_WIDTH, 
                    SCREEN_HEIGHT
                )
            )
        else:
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    SCREEN_WIDTH // 2, 
                    SCREEN_HEIGHT // 2, 
                    SCREEN_WIDTH, 
                    SCREEN_HEIGHT
                ),
                (20, 20, 40)
            )
        
        # Отрисовка кнопок
        for button in self.button_list:
            # Определяем цвет кнопки
            if self.pressed_button == button:
                color = BUTTON_PRESSED
            elif self.hovered_button == button:
                color = BUTTON_HOVER
            else:
                color = BUTTON_NORMAL
            
            # Рисуем кнопку
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    button["x"] + button["width"] // 2,
                    button["y"] + button["height"] // 2,
                    button["width"],
                    button["height"]
                ),
                color
            )
            
            # Рамка кнопки
            arcade.draw_rect_outline(
                arcade.rect.XYWH(
                    button["x"] + button["width"] // 2,
                    button["y"] + button["height"] // 2,
                    button["width"],
                    button["height"]
                ),
                BUTTON_BORDER,
                2
            )
            
            # Текст кнопки
            arcade.draw_text(
                button["text"],
                button["x"] + button["width"] // 2,
                button["y"] + button["height"] // 2,
                TEXT_COLOR,
                20,
                anchor_x="center",
                anchor_y="center",
                font_name=("Arial", "arial"),
                bold=True
            )
    
    def on_mouse_motion(self, x, y, dx, dy):
        self.hovered_button = None
        for button in self.button_list:
            if (button["x"] <= x <= button["x"] + button["width"] and 
                button["y"] <= y <= button["y"] + button["height"]):
                self.hovered_button = button
                break
    
    def on_mouse_press(self, x, y, button, modifiers):
        self.pressed_button = None
        for btn in self.button_list:
            if (btn["x"] <= x <= btn["x"] + btn["width"] and 
                btn["y"] <= y <= btn["y"] + btn["height"]):
                self.pressed_button = btn
                break
    
    def on_mouse_release(self, x, y, button, modifiers):
        if self.pressed_button:
            for btn in self.button_list:
                if (btn["x"] <= x <= btn["x"] + btn["width"] and 
                    btn["y"] <= y <= btn["y"] + btn["height"] and 
                    btn == self.pressed_button):
                    
                    if btn["action"] == "start":
                        # Переход к выбору этажа
                        floor_view = FloorSelectionView()
                        floor_view.setup()
                        self.window.show_view(floor_view)
                    elif btn["action"] == "exit":
                        arcade.exit()
                    break
        
        self.pressed_button = None


# ============== ВЫБОР ЭТАЖА ==============
class FloorSelectionView(arcade.View):
    def __init__(self):
        super().__init__()
        self.button_list = []
        self.hovered_button = None
        self.pressed_button = None
        self.floor_images = {
            1: "First_Floor",
            2: "Second_Floor", 
            3: "Third_Floor"
        }
        self.showing_floor_image = False
        self.floor_image_start_time = 0
        self.selected_floor = None
        self.floor_textures = {}
        
    def setup(self):
        # Загружаем текстуры этажей
        for floor_num, image_name in self.floor_images.items():
            try:
                texture = arcade.load_texture(f"data/images/{image_name}.png")
                self.floor_textures[floor_num] = texture
            except:
                self.floor_textures[floor_num] = arcade.Texture.create_empty(
                    f"floor_{floor_num}",
                    (SCREEN_WIDTH, SCREEN_HEIGHT)
                )
        
        # Создаем кнопки выбора этажа
        button_width = 340
        button_height = 50
        
        # Этаж 1
        floor1_button = {
            "x": SCREEN_WIDTH // 2 - button_width // 2,
            "y": SCREEN_HEIGHT // 2 + 60,
            "width": button_width,
            "height": button_height,
            "text": "ЭТАЖ 1: КРЕПОСТНАЯ СТЕНА",
            "floor": 1,
            "locked": False
        }
        self.button_list.append(floor1_button)
        
        # Этаж 2
        floor2_button = {
            "x": SCREEN_WIDTH // 2 - button_width // 2,
            "y": SCREEN_HEIGHT // 2 - 15,
            "width": button_width,
            "height": button_height,
            "text": "ЭТАЖ 2: ЦИТАДЕЛЬ",
            "floor": 2,
            "locked": False
        }
        self.button_list.append(floor2_button)
        
        # Этаж 3
        floor3_button = {
            "x": SCREEN_WIDTH // 2 - button_width // 2,
            "y": SCREEN_HEIGHT // 2 - 90,
            "width": button_width,
            "height": button_height,
            "text": "ЭТАЖ 3: ПОДЗЕМЕЛЬЕ",
            "floor": 3,
            "locked": True
        }
        self.button_list.append(floor3_button)
        
        # Кнопка обучения
        tutorial_button = {
            "x": SCREEN_WIDTH // 2 - button_width // 2,
            "y": SCREEN_HEIGHT // 2 - 165,
            "width": button_width,
            "height": 40,
            "text": "ОБУЧЕНИЕ",
            "action": "tutorial"
        }
        self.button_list.append(tutorial_button)
        
        # Кнопка сюжета
        story_button = {
            "x": SCREEN_WIDTH // 2 - button_width // 2,
            "y": SCREEN_HEIGHT // 2 - 210,
            "width": button_width,
            "height": 40,
            "text": "СЮЖЕТ",
            "action": "story"
        }
        self.button_list.append(story_button)
        
        # Кнопка возврата
        back_button = {
            "x": 20,
            "y": 20,
            "width": 140,
            "height": 40,
            "text": "НАЗАД",
            "action": "back"
        }
        self.button_list.append(back_button)
    
    def on_draw(self):
        self.clear()
        
        # Фон на весь экран
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                SCREEN_WIDTH // 2, 
                SCREEN_HEIGHT // 2, 
                SCREEN_WIDTH, 
                SCREEN_HEIGHT
            ),
            (20, 20, 40)
        )
        
        # Заголовок
        arcade.draw_text(
            "ВЫБОР ЭТАЖА", 
            SCREEN_WIDTH // 2, 
            SCREEN_HEIGHT - 70,
            (255, 215, 0),
            36,
            anchor_x="center",
            anchor_y="center",
            font_name=("Arial", "arial"),
            bold=True
        )
        
        # Отрисовка кнопок
        for button in self.button_list:
            # Определяем цвет кнопки
            if button.get("locked", False):
                color = (50, 50, 50, 255)
                text_color = (100, 100, 100, 255)
            elif self.pressed_button == button:
                color = BUTTON_PRESSED
                text_color = TEXT_COLOR
            elif self.hovered_button == button:
                color = BUTTON_HOVER
                text_color = TEXT_COLOR
            else:
                color = BUTTON_NORMAL
                text_color = TEXT_COLOR
            
            # Рисуем кнопку
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    button["x"] + button["width"] // 2,
                    button["y"] + button["height"] // 2,
                    button["width"],
                    button["height"]
                ),
                color
            )
            
            # Рамка кнопки
            arcade.draw_rect_outline(
                arcade.rect.XYWH(
                    button["x"] + button["width"] // 2,
                    button["y"] + button["height"] // 2,
                    button["width"],
                    button["height"]
                ),
                BUTTON_BORDER,
                2
            )
            
            # Текст кнопки
            text_size = 16 if "floor" in button else 14
            arcade.draw_text(
                button["text"],
                button["x"] + button["width"] // 2,
                button["y"] + button["height"] // 2,
                text_color,
                text_size,
                anchor_x="center",
                anchor_y="center",
                font_name=("Arial", "arial"),
                bold=True
            )
            
            # Иконка для заблокированного этажа
            if button.get("locked", False):
                arcade.draw_text(
                    "🔒",
                    button["x"] + button["width"] - 20,
                    button["y"] + button["height"] // 2,
                    text_color,
                    20,
                    anchor_x="center",
                    anchor_y="center",
                    font_name=("Arial", "arial")
                )
        
        # Если показываем изображение этажа
        if self.showing_floor_image and self.selected_floor:
            current_time = time.time()
            if current_time - self.floor_image_start_time < 2:
                # Прозрачный черный фон на весь экран
                arcade.draw_rect_filled(
                    arcade.rect.XYWH(
                        SCREEN_WIDTH // 2, 
                        SCREEN_HEIGHT // 2, 
                        SCREEN_WIDTH, 
                        SCREEN_HEIGHT
                    ),
                    (0, 0, 0, 220)
                )
                
                texture = self.floor_textures.get(self.selected_floor)
                if texture and texture.width > 1:
                    scale = min(
                        SCREEN_WIDTH / texture.width * 0.8, 
                        SCREEN_HEIGHT / texture.height * 0.8
                    )
                    
                    texture_rect = arcade.rect.XYWH(
                        SCREEN_WIDTH // 2,
                        SCREEN_HEIGHT // 2,
                        texture.width * scale,
                        texture.height * scale
                    )
                    
                    arcade.draw_texture_rect(texture, texture_rect)
                else:
                    colors = {
                        1: (139, 69, 19),
                        2: (105, 105, 105),
                        3: (47, 79, 79)
                    }
                    color = colors.get(self.selected_floor, (128, 128, 128))
                    
                    arcade.draw_rect_filled(
                        arcade.rect.XYWH(
                            SCREEN_WIDTH // 2,
                            SCREEN_HEIGHT // 2,
                            SCREEN_WIDTH * 0.8,
                            SCREEN_HEIGHT * 0.6
                        ),
                        color
                    )
                
                floor_names = {
                    1: "КРЕПОСТНАЯ СТЕНА",
                    2: "ЦИТАДЕЛЬ",
                    3: "ПОДЗЕМЕЛЬЕ"
                }
                
                arcade.draw_text(
                    f"ЭТАЖ {self.selected_floor}: {floor_names.get(self.selected_floor, '')}",
                    SCREEN_WIDTH // 2, 
                    SCREEN_HEIGHT - 90,
                    (255, 215, 0),
                    28,
                    anchor_x="center", 
                    anchor_y="center",
                    font_name=("Arial", "arial"),
                    bold=True
                )
                
                arcade.draw_text(
                    "ЗАГРУЗКА УРОВНЯ...",
                    SCREEN_WIDTH // 2, 
                    70,
                    (255, 255, 255),
                    20,
                    anchor_x="center", 
                    anchor_y="center",
                    font_name=("Arial", "arial"),
                    bold=True
                )
                
            else:
                # Через 2 секунды переходим к игре или интро
                self.showing_floor_image = False
                # Для первого этажа показываем интро, для остальных - сразу игру
                if self.selected_floor == 1:
                    intro_view = IntroView(self.selected_floor)
                    intro_view.setup()
                    self.window.show_view(intro_view)
                else:
                    game_view = GameView()
                    game_view.setup(self.selected_floor)
                    self.window.show_view(game_view)
    
    def on_mouse_motion(self, x, y, dx, dy):
        if not self.showing_floor_image:
            self.hovered_button = None
            for button in self.button_list:
                if (button["x"] <= x <= button["x"] + button["width"] and 
                    button["y"] <= y <= button["y"] + button["height"]):
                    self.hovered_button = button
                    break
    
    def on_mouse_press(self, x, y, button, modifiers):
        if not self.showing_floor_image:
            self.pressed_button = None
            for btn in self.button_list:
                if (btn["x"] <= x <= btn["x"] + btn["width"] and 
                    btn["y"] <= y <= btn["y"] + btn["height"]):
                    self.pressed_button = btn
                    break
    
    def on_mouse_release(self, x, y, button, modifiers):
        if self.showing_floor_image:
            return
            
        if self.pressed_button:
            for btn in self.button_list:
                if (btn["x"] <= x <= btn["x"] + btn["width"] and 
                    btn["y"] <= y <= btn["y"] + btn["height"] and 
                    btn == self.pressed_button):
                    
                    if "action" in btn and btn["action"] == "back":
                        menu_view = MainMenuView()
                        menu_view.setup()
                        self.window.show_view(menu_view)
                    
                    elif "action" in btn and btn["action"] == "tutorial":
                        # Переход к обучению
                        tutorial_view = TutorialView(self)
                        tutorial_view.setup()
                        self.window.show_view(tutorial_view)
                    
                    elif "action" in btn and btn["action"] == "story":
                        # Переход к сюжету
                        story_view = StoryView(self)
                        story_view.setup()
                        self.window.show_view(story_view)
                    
                    elif "floor" in btn:
                        if btn.get("locked", False):
                            pass
                        else:
                            self.selected_floor = btn["floor"]
                            self.showing_floor_image = True
                            self.floor_image_start_time = time.time()
                    
                    break
        
        self.pressed_button = None


# ============== ИГРОВОЙ УРОВЕНЬ ==============
class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.attack_hitboxes = []
        self.sword_slashes = []
        self.keys_held = set()
        self.background_texture = None
        self.show_tutorial_button = True
        
        # Новые атрибуты для столкновений
        self.wall_sprites = None
        self.door_sprites = None
        self.floor = None
        self.room_cleared = False
        self.door_open = False  # ДОБАВЛЕНО: инициализация атрибута
    
    def setup(self, floor_number=1):
        self.floor_number = floor_number
        self.lives = 3
        self.room_cleared = False  # ДОБАВЛЕНО: инициализация
        self.door_open = False     # ДОБАВЛЕНО: инициализация
        
        # Загрузка фона
        try:
            self.background_texture = arcade.load_texture("assets/backgrounds/WallFirst.png")
        except:
            self.background_texture = None
        
        # Инициализация игрока
        self.player = Player()
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player.sprite)
        
        # Инициализация списков спрайтов
        self.enemy_sprites = arcade.SpriteList()
        self.wall_sprites = arcade.SpriteList()
        self.door_sprites = arcade.SpriteList()
        self.current_enemies = []
        self.current_projectiles = []
        self.current_pickups = []
        
        # Создаем этаж с сеткой комнат
        self.floor = Floor(floor_number, size=3)
        
        # Загружаем текущую комнату
        self._load_current_room()
    
    def _load_current_room(self):
        # Очищаем все спрайты
        self.enemy_sprites.clear()
        self.wall_sprites.clear()
        self.door_sprites.clear()
        self.current_enemies.clear()
        self.current_projectiles.clear()
        self.current_pickups.clear()
        
        room = self.floor.get_current_room()
        
        # Создаем стены (границы комнаты)
        self._create_walls()
        
        # Создаем препятствия (коробки/камни)
        self._create_obstacles(room)
        
        # Создаем двери (пока закрытые)
        self._create_doors(room)
        
        # Спавним врагов
        self._spawn_enemies(room)
        
        # Спавним сердце в случайных комнатах
        if random.random() > 0.7 and room.type != RoomType.START and room.type != RoomType.BOSS:
            x, y = self.find_free_position()
            self.current_pickups.append(Heart(x, y))
        
        # Позиция игрока
        if room.type == RoomType.START:
            self.player.sprite.center_x = SCREEN_WIDTH // 2
            self.player.sprite.center_y = 140
        else:
            # Определяем, из какой двери пришел игрок
            self._position_player_at_door()
        
        # Определяем, очищена ли комната и открыты ли двери
        self.room_cleared = len(self.current_enemies) == 0
        self.door_open = self.room_cleared or room.type == RoomType.START
        
        # Обновляем состояние дверей
        self._update_doors_state()
    
    def _create_walls(self):
        # Верхняя и нижняя стены
        for x in range(0, SCREEN_WIDTH, WALL_TILE):
            # Нижняя стена
            wall = arcade.SpriteSolidColor(WALL_TILE, WALL_TILE, arcade.color.DARK_BROWN)
            wall.center_x = x + WALL_TILE // 2
            wall.center_y = WALL_TILE // 2
            self.wall_sprites.append(wall)
            
            # Верхняя стена
            wall = arcade.SpriteSolidColor(WALL_TILE, WALL_TILE, arcade.color.DARK_BROWN)
            wall.center_x = x + WALL_TILE // 2
            wall.center_y = SCREEN_HEIGHT - WALL_TILE // 2
            self.wall_sprites.append(wall)
        
        # Левая и правая стены
        for y in range(WALL_TILE, SCREEN_HEIGHT - WALL_TILE, WALL_TILE):
            # Левая стена
            wall = arcade.SpriteSolidColor(WALL_TILE, WALL_TILE, arcade.color.DARK_BROWN)
            wall.center_x = WALL_TILE // 2
            wall.center_y = y + WALL_TILE // 2
            self.wall_sprites.append(wall)
            
            # Правая стена
            wall = arcade.SpriteSolidColor(WALL_TILE, WALL_TILE, arcade.color.DARK_BROWN)
            wall.center_x = SCREEN_WIDTH - WALL_TILE // 2
            wall.center_y = y + WALL_TILE // 2
            self.wall_sprites.append(wall)
    
    def _create_obstacles(self, room):
        def is_position_allowed(x, y):
            # Проверяем запретные зоны
            for fx, fy, r in room.forbidden_zones:
                if math.sqrt((x - fx) ** 2 + (y - fy) ** 2) < r:
                    return False
            
            # Проверяем расстояние до игрока
            if room.type == RoomType.START:
                if math.sqrt((x - SCREEN_WIDTH // 2) ** 2 + (y - 140) ** 2) < 120:
                    return False
            
            return True
        
        # Создаем случайные препятствия (коробки)
        if room.type != RoomType.BOSS:  # В комнате босса меньше препятствий
            # Уменьшенное количество препятствий
            if room.type == RoomType.NORMAL:
                obstacle_count = random.randint(1, 3)  # Было 3-8
            else:
                obstacle_count = 1  # Было 2
            
            for _ in range(obstacle_count):
                placed = False
                attempts = 0
                
                while not placed and attempts < 50:
                    attempts += 1
                    x = random.randint(120, SCREEN_WIDTH - 120)  # Уменьшены границы
                    y = random.randint(120, SCREEN_HEIGHT - 120)
                    
                    if not is_position_allowed(x, y):
                        continue
                    
                    # Проверяем столкновения с существующими стенами
                    temp_box = arcade.SpriteSolidColor(50, 50, arcade.color.DARK_BROWN)  # Уменьшен размер
                    temp_box.center_x = x
                    temp_box.center_y = y
                    
                    if not arcade.check_for_collision_with_list(temp_box, self.wall_sprites):
                        # Создаем коробку
                        try:
                            box = arcade.Sprite("assets/sprites/box.png", scale=0.12)  # Уменьшен масштаб
                        except:
                            box = arcade.SpriteSolidColor(50, 50, arcade.color.BROWN)
                        
                        box.center_x = x
                        box.center_y = y
                        self.wall_sprites.append(box)
                        placed = True
    
    def _create_doors(self, room):
        margin = 60  # Уменьшено
        
        for direction in room.doors:
            if direction == "up":
                x = SCREEN_WIDTH // 2
                y = SCREEN_HEIGHT - margin
            elif direction == "down":
                x = SCREEN_WIDTH // 2
                y = margin
            elif direction == "left":
                x = margin
                y = SCREEN_HEIGHT // 2
            elif direction == "right":
                x = SCREEN_WIDTH - margin
                y = SCREEN_HEIGHT // 2
            else:
                continue
            
            # Создаем спрайт двери
            try:
                door = arcade.Sprite("assets/sprites/door.png", scale=0.08)  # Уменьшен масштаб
            except:
                door = arcade.SpriteSolidColor(50, 80, arcade.color.DARK_BROWN)  # Уменьшен размер
            
            door.center_x = x
            door.center_y = y
            door.direction = direction
            # Изначально все двери закрыты, состояние обновится позже
            door.is_open = False
            self.door_sprites.append(door)
    
    def _update_doors_state(self):
        """Обновляет состояние дверей (открыты/закрыты)"""
        for door in self.door_sprites:
            door.is_open = self.door_open
            # Если дверь - цветной прямоугольник, меняем цвет
            if isinstance(door, arcade.SpriteSolidColor):
                if self.door_open:
                    door.color = arcade.color.LIGHT_GREEN
                else:
                    door.color = arcade.color.DARK_BROWN
    
    def _spawn_enemies(self, room):
        if room.type == RoomType.BOSS:
            # Спавним босса
            boss = Boss(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80)  # Уменьшена позиция
            self.current_enemies.append(boss)
            self.enemy_sprites.append(boss.sprite)
        else:
            # Спавним обычных врагов
            for spawn in room.enemy_spawns:
                x, y = self.find_free_position(min_y=150)  # Уменьшено
                enemy = Enemy(x, y)
                self.current_enemies.append(enemy)
                self.enemy_sprites.append(enemy.sprite)
    
    def _position_player_at_door(self):
        # Эта функция должна определять, из какой двери пришел игрок
        # Для простоты всегда ставим игрока в центре снизу
        self.player.sprite.center_x = SCREEN_WIDTH // 2
        self.player.sprite.center_y = 140  # Уменьшено
    
    def find_free_position(self, min_x=120, max_x=None, min_y=120, max_y=None, tries=50):
        if max_x is None:
            max_x = SCREEN_WIDTH - 120  # Уменьшено
        if max_y is None:
            max_y = SCREEN_HEIGHT - 120  # Уменьшено
        
        for _ in range(tries):
            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)
            
            # Создаем временный спрайт для проверки столкновений
            temp = arcade.SpriteSolidColor(32, 32, arcade.color.RED)  # Уменьшен размер
            temp.center_x = x
            temp.center_y = y
            
            if not arcade.check_for_collision_with_list(temp, self.wall_sprites):
                return x, y
        
        # Если не нашли свободное место, возвращаем центр
        return SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    
    def on_draw(self):
        self.clear()
        
        # Фон на весь экран
        if self.background_texture:
            arcade.draw_texture_rect(
                self.background_texture,
                arcade.rect.XYWH(
                    SCREEN_WIDTH // 2,
                    SCREEN_HEIGHT // 2,
                    SCREEN_WIDTH,
                    SCREEN_HEIGHT
                )
            )
        else:
            arcade.draw_lbwh_rectangle_filled(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.DARK_SLATE_GRAY)
        
        # Отрисовка объектов
        self.wall_sprites.draw()  # Стены и коробки
        self.door_sprites.draw()  # Двери
        self.player_list.draw()
        
        for heart in self.current_pickups:
            heart.draw()
            
        for proj in list(self.current_projectiles):
            proj.draw()
            
        self.enemy_sprites.draw()
        
        for slash in self.sword_slashes:
            arcade.draw_line(
                slash["x1"], slash["y1"],
                slash["x2"], slash["y2"],
                arcade.color.WHITE,
                4  # Уменьшена толщина
            )

        # Кнопка обучения
        tutorial_button_x = SCREEN_WIDTH - 80  # Уменьшено
        tutorial_button_y = SCREEN_HEIGHT - 25  # Уменьшено
        
        arcade.draw_circle_filled(tutorial_button_x, tutorial_button_y, 16, (87, 76, 41))  # Уменьшен радиус
        arcade.draw_circle_outline(tutorial_button_x, tutorial_button_y, 16, BUTTON_BORDER, 1)  # Уменьшен радиус
        arcade.draw_text("?", tutorial_button_x, tutorial_button_y, 
                        TEXT_COLOR, 20, anchor_x="center", anchor_y="center",  # Уменьшен размер
                        font_name=("Arial", "arial"), bold=True)
        
        arcade.draw_text("F1", tutorial_button_x, tutorial_button_y - 30,  # Уменьшено
                        arcade.color.LIGHT_GRAY, 14, anchor_x="center", anchor_y="center",  # Уменьшен размер
                        font_name=("Arial", "arial"))

        # HUD
        room = self.floor.get_current_room()
        room_type_text = ""
        if room.type == RoomType.START:
            room_type_text = "СТАРТ"
        elif room.type == RoomType.BOSS:
            room_type_text = "БОСС"
        else:
            room_type_text = f"КОМНАТА {self.floor.current_pos[0] + 1}-{self.floor.current_pos[1] + 1}"
        
        arcade.draw_text(f"HP: {int(self.player.hp)}/{self.player.max_hp}", 15, SCREEN_HEIGHT - 30, 
                       arcade.color.WHITE, 22)  # Уменьшен размер
        
        # Жизни сердечками
        heart_spacing = 32  # Уменьшено
        for i in range(self.lives):
            matrix_w = len(HEART_MATRIX[0]) * PIXEL
            matrix_h = len(HEART_MATRIX) * PIXEL
            x = 20 + matrix_w // 2 + i * heart_spacing
            y = SCREEN_HEIGHT - 70 - matrix_h // 2  # Уменьшено
            top_left_x = x - matrix_w // 2
            top_left_y = y + matrix_h // 2
            draw_pixel_matrix(HEART_MATRIX, top_left_x, top_left_y, arcade.color.RED)
        
        arcade.draw_text(room_type_text, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30,
                       arcade.color.WHITE, 20, anchor_x="center")  # Уменьшен размер
        
        arcade.draw_text(f"Этаж {self.floor_number}", SCREEN_WIDTH - 130, SCREEN_HEIGHT - 30,  # Уменьшено
                       arcade.color.WHITE, 20)  # Уменьшен размер

        # Здоровье босса
        if any(isinstance(e, Boss) for e in self.current_enemies):
            boss = next(e for e in self.current_enemies if isinstance(e, Boss))
            bar_w = 450  # Уменьшено
            x = (SCREEN_WIDTH - bar_w) // 2
            y = SCREEN_HEIGHT - 60  # Уменьшено
            ratio = max(0.0, boss.hp / boss.max_hp)
            arcade.draw_lbwh_rectangle_filled(x, y - 7, int(bar_w * ratio), 14, arcade.color.RED)  # Уменьшена высота
            arcade.draw_lrbt_rectangle_outline(x, x + bar_w, y - 7, y + 7, arcade.color.WHITE)  # Уменьшена высота
            
            # Фаза босса
            arcade.draw_text(f"Фаза: {boss.phase}", x + bar_w // 2, y - 30,  # Уменьшено
                           arcade.color.YELLOW, 16, anchor_x="center")  # Уменьшен размер
        
        # Подсказка для дверей
        if self.door_open and self.floor.get_current_room().type != RoomType.BOSS:
            arcade.draw_text("E - войти в дверь", SCREEN_WIDTH // 2, 40,  # Уменьшено
                           arcade.color.LIGHT_GREEN, 18, anchor_x="center")  # Уменьшен размер
    
    def on_update(self, dt):
        # Движение игрока с проверкой столкновений
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

            # Двигаем по X и проверяем столкновения
            old_x = self.player.sprite.center_x
            self.player.sprite.center_x += dx * self.player.speed * dt
            if arcade.check_for_collision_with_list(self.player.sprite, self.wall_sprites):
                self.player.sprite.center_x = old_x

            # Двигаем по Y и проверяем столкновений
            old_y = self.player.sprite.center_y
            self.player.sprite.center_y += dy * self.player.speed * dt
            if arcade.check_for_collision_with_list(self.player.sprite, self.wall_sprites):
                self.player.sprite.center_y = old_y

            # Ограничение по экрану (на всякий случай)
            self.player.sprite.center_x = max(20, min(SCREEN_WIDTH - 20, self.player.sprite.center_x))
            self.player.sprite.center_y = max(20, min(SCREEN_HEIGHT - 20, self.player.sprite.center_y))

            # Поворот спрайта
            if dx > 0:
                self.player.sprite.scale_x = abs(self.player.sprite.scale_x)
            elif dx < 0:
                self.player.sprite.scale_x = -abs(self.player.sprite.scale_x)

        self.player.update(dt)

        # Обновляем врагов с проверкой столкновений
        for e in list(self.current_enemies):
            if isinstance(e, Boss):
                e.update(self.player, dt, self.current_projectiles, self.wall_sprites)
            else:
                e.update(self.player, dt, self.wall_sprites)

            # Контактный урон
            if abs(e.x - self.player.x) < 25 and abs(e.y - self.player.y) < 25:  # Уменьшено
                self.player.hp -= 30 * dt

            if e.hp <= 0:
                self.current_enemies.remove(e)
                self.enemy_sprites.remove(e.sprite)

        # Обновляем снаряды
        for proj in list(self.current_projectiles):
            proj.update(dt)
            if proj.x < -150 or proj.x > SCREEN_WIDTH + 150 or proj.y < -150 or proj.y > SCREEN_HEIGHT + 150:  # Уменьшено
                if proj in self.current_projectiles:
                    self.current_projectiles.remove(proj)
                continue
            
            # Столкновение снаряда с игроком
            if abs(proj.x - self.player.x) < 12 and abs(proj.y - self.player.y) < 12:  # Уменьшено
                self.player.hp -= proj.damage
                if proj in self.current_projectiles:
                    self.current_projectiles.remove(proj)
            
            # Столкновение снаряда со стенами
            temp_proj = arcade.SpriteSolidColor(6, 6, arcade.color.YELLOW)  # Уменьшен размер
            temp_proj.center_x = proj.x
            temp_proj.center_y = proj.y
            if arcade.check_for_collision_with_list(temp_proj, self.wall_sprites):
                if proj in self.current_projectiles:
                    self.current_projectiles.remove(proj)

        # Подбор предметов
        for heart in list(self.current_pickups):
            if abs(heart.x - self.player.x) < 25 and abs(heart.y - self.player.y) < 25:  # Уменьшено
                self.player.max_hp += 20
                self.player.hp = min(self.player.max_hp, self.player.hp + 40)
                self.current_pickups.remove(heart)

        # Проверка зачистки комнаты
        if not self.current_enemies and not self.room_cleared:
            self.room_cleared = True
            self.door_open = True
            self._update_doors_state()
        
        # Обновляем анимацию удара
        for slash in self.sword_slashes[:]:
            slash["time"] -= dt
            if slash["time"] <= 0:
                self.sword_slashes.remove(slash)

        # Проверка смерти игрока
        if self.player.hp <= 0:
            self.lives -= 1
            
            if self.lives > 0:
                # Перезагружаем текущую комнату
                self.player.hp = self.player.max_hp
                self._load_current_room()
            else:
                # Возвращаемся к выбору этажа
                floor_view = FloorSelectionView()
                floor_view.setup()
                self.window.show_view(floor_view)
    
    def on_key_press(self, key, modifiers):
        self.keys_held.add(key)

        # АТАКА
        if key in (arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT):
            if not self.player.can_attack():
                return

            self.player.attack_timer = self.player.attack_cooldown

            reach = 55  # Уменьшено
            half_w = 36  # Уменьшено
            half_h = 36  # Уменьшено

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

            for e in list(self.current_enemies):
                if abs(e.x - hx) < half_w and abs(e.y - hy) < half_h:
                    e.hp -= 30

            # Визуализация удара
            if key == arcade.key.UP:
                line = (self.player.x - 50, self.player.y + 32,  # Уменьшено
                        self.player.x + 50, self.player.y + 32)
            elif key == arcade.key.DOWN:
                line = (self.player.x - 50, self.player.y - 32,  # Уменьшено
                        self.player.x + 50, self.player.y - 32)
            elif key == arcade.key.LEFT:
                line = (self.player.x - 50, self.player.y - 32,  # Уменьшено
                        self.player.x - 50, self.player.y + 32)
            else:
                line = (self.player.x + 50, self.player.y - 32,  # Уменьшено
                        self.player.x + 50, self.player.y + 32)

            self.sword_slashes.append({
                "x1": line[0],
                "y1": line[1],
                "x2": line[2],
                "y2": line[3],
                "time": 0.12
            })

        # ВЗАИМОДЕЙСТВИЕ С ДВЕРЬЮ
        if key == arcade.key.E and self.door_open:
            # Проверяем столкновение с дверьми
            for door in self.door_sprites:
                if arcade.check_for_collision(self.player.sprite, door):
                    if self.floor.move(door.direction):
                        self._load_current_room()
                    break

        # КЛАВИША ОБУЧЕНИЯ
        if key == arcade.key.F1:
            tutorial_view = TutorialView(self)
            tutorial_view.setup()
            self.window.show_view(tutorial_view)

        # ВЫХОД В МЕНЮ
        if key == arcade.key.ESCAPE:
            menu_view = MainMenuView()
            menu_view.setup()
            self.window.show_view(menu_view)
    
    def on_mouse_press(self, x, y, button, modifiers):
        tutorial_button_x = SCREEN_WIDTH - 80  # Обновлено
        tutorial_button_y = SCREEN_HEIGHT - 25  # Обновлено
        distance = math.sqrt((x - tutorial_button_x) ** 2 + (y - tutorial_button_y) ** 2)
        
        if distance <= 16:  # Обновлено
            tutorial_view = TutorialView(self)
            tutorial_view.setup()
            self.window.show_view(tutorial_view)
    
    def on_key_release(self, key, modifiers):
        self.keys_held.discard(key)


# ============== ГЛАВНОЕ ОКНО ==============
class GameWindow(arcade.Window):
    def __init__(self):
        # ИЗМЕНЕНО: Используем оконный режим 1024x768 вместо полноэкранного
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=False)
        arcade.set_background_color((0, 0, 0))
    
    def setup(self):
        menu_view = MainMenuView()
        menu_view.setup()
        self.show_view(menu_view)


# ============== ЗАПУСК ==============
def main():
    window = GameWindow()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()