import arcade
import random
from PIL import Image
import time
from src.player import Player
from src.dungeon import Floor
from src.enemy import *
from src.boss import *
from src.settings import *


class Heart(arcade.Sprite):
    _texture = None
    
    def __init__(self, x, y):
        texture = Heart.get_heart_texture()
        super().__init__(texture=texture)
        self.center_x = x
        self.center_y = y
        self.pickup_type = "heart"
        self.scale = 0.5
    
    @classmethod
    def get_heart_texture(cls):
        if cls._texture is None:
            cls._texture = cls._create_heart_texture()
        return cls._texture
    
    @staticmethod
    def _create_heart_texture():
        matrix = HEART_MATRIX
        width = len(matrix[0]) * PIXEL
        height = len(matrix) * PIXEL
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        pixels = img.load()
        
        for r, row in enumerate(matrix):
            for c, cell in enumerate(row):
                if cell == "1":
                    for px in range(PIXEL):
                        for py in range(PIXEL):
                            x_pos = c * PIXEL + px
                            y_pos = height - (r * PIXEL + py) - 1
                            if 0 <= x_pos < width and 0 <= y_pos < height:
                                pixels[x_pos, y_pos] = (255, 105, 180, 255)
        
        return arcade.Texture.create_filled(
            f"heart_{width}x{height}",
            (width, height),
            color_list=Heart._image_to_color_list(img)
        )
    
    @staticmethod
    def _image_to_color_list(img):
        width, height = img.size
        data = img.load()
        colors = []
        
        for y in range(height):
            for x in range(width):
                pixel = data[x, y]
                colors.append(pixel)
        
        return colors

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
                     "Поднявшись выше, рыцарь попадает в цитадель.",
                     "Здесь когда-то решались судьбы королевства,",
                     "но теперь лишь тени прошлого бродят по залам.",
                     "Что-то знакомое есть в этих стенах,",
                     "но память по-прежнему молчит."
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
        back_button = {
            "x": 30,
            "y": 30,
            "width": 150,
            "height": 40,
            "text": "НАЗАД",
            "action": "back"
        }
        self.button_list.append(back_button)
        
        prev_button = {
            "x": SCREEN_WIDTH // 2 - 180,
            "y": 80,
            "width": 160,
            "height": 40,
            "text": "ПРЕДЫДУЩАЯ",
            "action": "prev"
        }
        self.button_list.append(prev_button)
        
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
        
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                SCREEN_WIDTH // 2, 
                SCREEN_HEIGHT // 2, 
                SCREEN_WIDTH, 
                SCREEN_HEIGHT
            ),
            (20, 20, 40)
        )
        
        page = self.pages[self.current_page]
        
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
        
        for button in self.button_list:
            if self.pressed_button == button:
                color = BUTTON_PRESSED
            elif self.hovered_button == button:
                color = BUTTON_HOVER
            else:
                color = BUTTON_NORMAL
            
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    button["x"] + button["width"] // 2,
                    button["y"] + button["height"] // 2,
                    button["width"],
                    button["height"]
                ),
                color
            )
            
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
            self.window.show_view(self.previous_view)
        elif key == arcade.key.LEFT:
            if self.current_page > 0:
                self.current_page -= 1
        elif key == arcade.key.RIGHT:
            if self.current_page < len(self.pages) - 1:
                self.current_page += 1

class IntroView(arcade.View):
    def __init__(self, floor_number):
        super().__init__()
        self.floor_number = floor_number
        self.button_list = []
        self.hovered_button = None
        self.pressed_button = None
        
    def setup(self):
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
        
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                SCREEN_WIDTH // 2, 
                SCREEN_HEIGHT // 2, 
                SCREEN_WIDTH, 
                SCREEN_HEIGHT
            ),
            (0, 0, 0)
        )
        
        intro_text_lines = [
            "Пробудившись ото сна длиною в тысячелетие,",
            "отважный рыцарь обнаружил себя",
            "в древних стенах забытого замка.",
            "Память была пуста, и лишь зовущее эхо прошлого",
            "вело его сквозь сумрак коридоров,",
            "чтобы восстановить нить событий."
        ]
        
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
        
        for button in self.button_list:
            if self.pressed_button == button:
                color = BUTTON_PRESSED
            elif self.hovered_button == button:
                color = BUTTON_HOVER
            else:
                color = BUTTON_NORMAL
            
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    button["x"] + button["width"] // 2,
                    button["y"] + button["height"] // 2,
                    button["width"],
                    button["height"]
                ),
                color
            )
            
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
                        game_view = GameView()
                        game_view.setup(self.floor_number)
                        self.window.show_view(game_view)
                    
                    break
        
        self.pressed_button = None
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER or key == arcade.key.SPACE:
            game_view = GameView()
            game_view.setup(self.floor_number)
            self.window.show_view(game_view)
        elif key == arcade.key.ESCAPE:
            floor_view = FloorSelectionView()
            floor_view.setup()
            self.window.show_view(floor_view)

class IntroLevel2View(arcade.View):
    def __init__(self, floor_number):
        super().__init__()
        self.floor_number = floor_number
        self.button_list = []
        self.hovered_button = None
        self.pressed_button = None
        
    def setup(self):
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
        
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                SCREEN_WIDTH // 2, 
                SCREEN_HEIGHT // 2, 
                SCREEN_WIDTH, 
                SCREEN_HEIGHT
            ),
            (0, 0, 0)
        )
        
        intro_text_lines = [
            "Второй этаж - Цитадель.",
            "",
            "Обрывки памяти возвращаются к вам.",
            "Эти стены... вы знали их тысячу лет назад.",
            "Именно здесь вы командовали войсками,",
            "которые разрушили эту крепость.",
            "",
            "Вы - не отважный рыцарь, а главный злодей,",
            "погрузившийся в сон после своей победы.",
            "Те, кого вы теперь встречаете - не враги,",
            "а потомки тех, кто пытался вас остановить.",
            "",
            "Продолжайте путь, чтобы вспомнить всё..."
        ]
        
        y_pos = SCREEN_HEIGHT // 2 + 120
        for i, line in enumerate(intro_text_lines):
            color = (255, 255, 255)
            font_size = 18
            if line.startswith("Второй этаж"):
                color = (255, 215, 0)
                font_size = 24
            elif line.startswith("Вы - не отважный"):
                color = (255, 100, 100)
                font_size = 20
            
            if line:
                arcade.draw_text(
                    line,
                    SCREEN_WIDTH // 2,
                    y_pos - i * 25,
                    color,
                    font_size,
                    anchor_x="center",
                    anchor_y="center",
                    font_name=("Arial", "arial"),
                    bold=(line.startswith("Второй этаж") or line.startswith("Вы - не отважный"))
                )
        
        for button in self.button_list:
            if self.pressed_button == button:
                color = BUTTON_PRESSED
            elif self.hovered_button == button:
                color = BUTTON_HOVER
            else:
                color = BUTTON_NORMAL
            
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    button["x"] + button["width"] // 2,
                    button["y"] + button["height"] // 2,
                    button["width"],
                    button["height"]
                ),
                color
            )
            
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
                        game_view = GameView()
                        game_view.setup(self.floor_number)
                        self.window.show_view(game_view)
                    
                    break
        
        self.pressed_button = None
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER or key == arcade.key.SPACE:
            game_view = GameView()
            game_view.setup(self.floor_number)
            self.window.show_view(game_view)
        elif key == arcade.key.ESCAPE:
            floor_view = FloorSelectionView()
            floor_view.setup()
            self.window.show_view(floor_view)

class IntroLevel3View(arcade.View):
    def __init__(self, floor_number):
        super().__init__()
        self.floor_number = floor_number
        self.button_list = []
        self.hovered_button = None
        self.pressed_button = None
        
    def setup(self):
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
        
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                SCREEN_WIDTH // 2, 
                SCREEN_HEIGHT // 2, 
                SCREEN_WIDTH, 
                SCREEN_HEIGHT
            ),
            (0, 0, 0)
        )
        
        intro_text_lines = [
            "Третий этаж - Подземелье.",
            "",
            "Теперь вы вспомнили всё.",
            "Вы не спасли эту крепость - вы её уничтожили.",
            "Ваша жажда власти привела к тысячелетнему проклятию,",
            "и вы заснули в троне повелителя тьмы.",
            "",
            "Эти стены пали от вашей руки.",
            "Души, которые вы встречаете - жертвы вашего гнева.",
            "Босс, которого вы должны победить - это отражение",
            "вашего собственного темного прошлого.",
            "",
            "Пришло время сделать выбор:",
            "Принять свою природу или искупить вину.",
        ]
        
        y_pos = SCREEN_HEIGHT // 2 + 120
        for i, line in enumerate(intro_text_lines):
            color = (255, 255, 255)
            font_size = 18
            if line.startswith("Третий этаж"):
                color = (255, 215, 0)
                font_size = 24
            elif line.startswith("Вы не спасли"):
                color = (255, 100, 100)
                font_size = 20
            elif line.startswith("Пришло время"):
                color = (100, 200, 255)
                font_size = 20
            
            if line:
                arcade.draw_text(
                    line,
                    SCREEN_WIDTH // 2,
                    y_pos - i * 25,
                    color,
                    font_size,
                    anchor_x="center",
                    anchor_y="center",
                    font_name=("Arial", "arial"),
                    bold=(line.startswith("Третий этаж") or line.startswith("Вы не спасли") or line.startswith("Пришло время"))
                )
        
        for button in self.button_list:
            if self.pressed_button == button:
                color = BUTTON_PRESSED
            elif self.hovered_button == button:
                color = BUTTON_HOVER
            else:
                color = BUTTON_NORMAL
            
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    button["x"] + button["width"] // 2,
                    button["y"] + button["height"] // 2,
                    button["width"],
                    button["height"]
                ),
                color
            )
            
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
                        game_view = GameView()
                        game_view.setup(self.floor_number)
                        self.window.show_view(game_view)
                    
                    break
        
        self.pressed_button = None
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER or key == arcade.key.SPACE:
            game_view = GameView()
            game_view.setup(self.floor_number)
            self.window.show_view(game_view)
        elif key == arcade.key.ESCAPE:
            floor_view = FloorSelectionView()
            floor_view.setup()
            self.window.show_view(floor_view)

class TutorialView(arcade.View):
    def __init__(self, previous_view):
        super().__init__()
        self.previous_view = previous_view
        self.button_list = []
        self.hovered_button = None
        self.pressed_button = None
        
    def setup(self):
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
        
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                SCREEN_WIDTH // 2, 
                SCREEN_HEIGHT // 2, 
                SCREEN_WIDTH, 
                SCREEN_HEIGHT
            ),
            (20, 20, 40)
        )
        
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
        
        tutorial_text = [
            "УПРАВЛЕНИЕ:",
            "W, A, S, D - движение",
            "Стрелки - атака в направлении",
            "LShift - рывок",
            "Пробел - щит (если есть)",
            "E - войти в дверь",
            "ESC - выход в меню",
            "",
            "СИСТЕМА ОРУЖИЯ:",
            "• На каждом уровне гарантированно появляется 2 разных оружия",
            "• Оружие находится в разных комнатах на уровне",
            "• На 2 и 3 уровнях также гарантированно появляется щит",
            "• Щит позволяет отражать снаряды врагов",
            "",
            "ПОДСКАЗКИ:",
            "• Используйте коробки для укрытия от врагов",
            "• Уклоняйтесь от снарядов босса",
            "• Двери откроются после уничтожения всех врагов",
            "• Исследуйте все комнаты для нахождения оружия",
            "• В сокровищницах можно найти дополнительное оружие"
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
            
            if line:
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
        
        for button in self.button_list:
            if self.pressed_button == button:
                color = BUTTON_PRESSED
            elif self.hovered_button == button:
                color = BUTTON_HOVER
            else:
                color = BUTTON_NORMAL
            
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    button["x"] + button["width"] // 2,
                    button["y"] + button["height"] // 2,
                    button["width"],
                    button["height"]
                ),
                color
            )
            
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
                        self.window.show_view(self.previous_view)
                    
                    break
        
        self.pressed_button = None
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.previous_view)

class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.button_list = []
        self.hovered_button = None
        self.pressed_button = None
        
    def setup(self):
        try:
            self.background_texture = arcade.load_texture("assets/Main_Background.png")
        except:
            self.background_texture = None
        
        button_width = 320
        button_height = 50
        
        start_button = {
            "x": SCREEN_WIDTH // 2 - button_width // 2,
            "y": SCREEN_HEIGHT // 2 - 30,
            "width": button_width,
            "height": button_height,
            "text": "НАЧАТЬ ИГРУ",
            "action": "start"
        }
        self.button_list.append(start_button)
        
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
        
        for button in self.button_list:
            if self.pressed_button == button:
                color = BUTTON_PRESSED
            elif self.hovered_button == button:
                color = BUTTON_HOVER
            else:
                color = BUTTON_NORMAL
            
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    button["x"] + button["width"] // 2,
                    button["y"] + button["height"] // 2,
                    button["width"],
                    button["height"]
                ),
                color
            )
            
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
                        floor_view = FloorSelectionView()
                        floor_view.setup()
                        self.window.show_view(floor_view)
                    elif btn["action"] == "exit":
                        arcade.exit()
                    break
        
        self.pressed_button = None

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
        for floor_num, image_name in self.floor_images.items():
            try:
                texture = arcade.load_texture(f"assets/{image_name}.png")
                self.floor_textures[floor_num] = texture
            except:
                self.floor_textures[floor_num] = arcade.Texture.create_empty(
                    f"floor_{floor_num}",
                    (SCREEN_WIDTH, SCREEN_HEIGHT)
                )
        
        button_width = 340
        button_height = 50
        
        floor1_completed = completed_levels[1]
        floor2_available = completed_levels[1]
        floor2_completed = completed_levels[2]
        floor3_available = completed_levels[1] and completed_levels[2]
        floor3_completed = completed_levels[3]
        
        floor1_button = {
            "x": SCREEN_WIDTH // 2 - button_width // 2,
            "y": SCREEN_HEIGHT // 2 + 60,
            "width": button_width,
            "height": button_height,
            "text": "ЭТАЖ 1: КРЕПОСТНАЯ СТЕНА",
            "floor": 1,
            "locked": False,
            "completed": floor1_completed
        }
        self.button_list.append(floor1_button)
        
        floor2_button = {
            "x": SCREEN_WIDTH // 2 - button_width // 2,
            "y": SCREEN_HEIGHT // 2 - 15,
            "width": button_width,
            "height": button_height,
            "text": "ЭТАЖ 2: ЦИТАДЕЛЬ",
            "floor": 2,
            "locked": not floor2_available,
            "completed": floor2_completed
        }
        self.button_list.append(floor2_button)
        
        floor3_button = {
            "x": SCREEN_WIDTH // 2 - button_width // 2,
            "y": SCREEN_HEIGHT // 2 - 90,
            "width": button_width,
            "height": button_height,
            "text": "ЭТАЖ 3: ПОДЗЕМЕЛЬЕ",
            "floor": 3,
            "locked": not floor3_available,
            "completed": floor3_completed
        }
        self.button_list.append(floor3_button)
        
        tutorial_button = {
            "x": SCREEN_WIDTH // 2 - button_width // 2,
            "y": SCREEN_HEIGHT // 2 - 165,
            "width": button_width,
            "height": 40,
            "text": "ОБУЧЕНИЕ",
            "action": "tutorial"
        }
        self.button_list.append(tutorial_button)
        
        story_button = {
            "x": SCREEN_WIDTH // 2 - button_width // 2,
            "y": SCREEN_HEIGHT // 2 - 210,
            "width": button_width,
            "height": 40,
            "text": "СЮЖЕТ",
            "action": "story"
        }
        self.button_list.append(story_button)
        
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
        
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                SCREEN_WIDTH // 2, 
                SCREEN_HEIGHT // 2, 
                SCREEN_WIDTH, 
                SCREEN_HEIGHT
            ),
            (20, 20, 40)
        )
        
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
        
        arcade.draw_text(
            "пройденные уровни горят зеленым",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 110,
            arcade.color.LIGHT_GREEN,
            18,
            anchor_x="center",
            anchor_y="center",
            font_name=("Arial", "arial")
        )
        
        for button in self.button_list:
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
            
            if button.get("completed", False):
                color = (50, 100, 50, 255)
            
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    button["x"] + button["width"] // 2,
                    button["y"] + button["height"] // 2,
                    button["width"],
                    button["height"]
                ),
                color
            )
            
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
        
        if self.showing_floor_image and self.selected_floor:
            current_time = time.time()
            if current_time - self.floor_image_start_time < 2:
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
                self.showing_floor_image = False
                if self.selected_floor == 1:
                    intro_view = IntroView(self.selected_floor)
                    intro_view.setup()
                    self.window.show_view(intro_view)
                elif self.selected_floor == 2:
                    intro_view = IntroLevel2View(self.selected_floor)
                    intro_view.setup()
                    self.window.show_view(intro_view)
                elif self.selected_floor == 3:
                    intro_view = IntroLevel3View(self.selected_floor)
                    intro_view.setup()
                    self.window.show_view(intro_view)
    
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
                        tutorial_view = TutorialView(self)
                        tutorial_view.setup()
                        self.window.show_view(tutorial_view)
                    
                    elif "action" in btn and btn["action"] == "story":
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

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.sword_slashes = []
        self.keys_held = set()
        self.background_texture = None
        self.show_tutorial_button = True
        self.wall_sprites = None
        self.door_sprites = None
        self.floor = None
        self.room_cleared = False
        self.door_open = False
        self.projectile_sprites = arcade.SpriteList()
        self.pickup_sprites = arcade.SpriteList()
        self.axe_swings = []
        self.halberd_swings = []
        self.hammer_swings = []
        self.notice_text = ""
        self.notice_timer = 0.0
        self.lives = 3
        self.screen_shake = 0

    def try_activate_shield(self):
        p = self.player
        if not p.has_shield or not p.shield_ready:
            return
        
        p.parry_active = True
        p.parry_timer = p.parry_window

        for arrow in self.projectile_sprites[:]:
            if not getattr(arrow, "from_enemy", False):
                continue

            dx = arrow.center_x - p.x
            dy = arrow.center_y - p.y
            dist = math.hypot(dx, dy)

            if dist <= p.shield_radius:
                arrow.remove_from_sprite_lists()

        p.shield_ready = False
        room = self.floor.get_current_room()
        if room.type == RoomType.BOSS:
            p.shield_time_cooldown = 7.0
        else:
            p.shield_room_cooldown = 2

    def setup(self, floor_number=1):
        self.floor_number = floor_number
        self.lives = 3
        self.room_cleared = False
        self.door_open = False
        
        try:
            self.background_texture = arcade.load_texture("assets/WallFirst.png")
        except:
            self.background_texture = None
        
        self.player = Player(SCREEN_WIDTH // 2, 190)
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player.sprite)
        
        self.enemy_sprites = arcade.SpriteList()
        self.wall_sprites = arcade.SpriteList()
        self.door_sprites = arcade.SpriteList()
        self.current_enemies = []
        self.projectile_sprites = arcade.SpriteList()
        self.pickup_sprites = arcade.SpriteList()
        
        self.floor = Floor(floor_number)
        
        self.load_current_room()
    
    def load_current_room(self):
        self.enemy_sprites.clear()
        self.wall_sprites.clear()
        self.door_sprites.clear()
        self.pickup_sprites.clear()
        self.projectile_sprites.clear()
        self.current_enemies.clear()
        self.sword_slashes.clear()
        self.axe_swings.clear()
        self.halberd_swings.clear()
        self.hammer_swings.clear()
        self.room_cleared = False
        self.notice_text = ""
        self.notice_timer = 0.0

        room = self.floor.get_current_room()
        room.add_forbidden_zone(SCREEN_WIDTH // 2, 190, 200)

        for x in range(0, SCREEN_WIDTH, WALL_TILE):
            rock = arcade.SpriteSolidColor(WALL_TILE, WALL_TILE, arcade.color.DARK_BROWN)
            rock.is_rock = False
            rock.is_wall = True
            rock.center_x = x + WALL_TILE // 2
            rock.center_y = WALL_TILE // 2
            self.wall_sprites.append(rock)
            
            rock2 = arcade.SpriteSolidColor(WALL_TILE, WALL_TILE, arcade.color.DARK_BROWN)
            rock2.is_rock = False
            rock2.is_wall = True
            rock2.center_x = x + WALL_TILE // 2
            rock2.center_y = SCREEN_HEIGHT - WALL_TILE // 2
            self.wall_sprites.append(rock2)
        
        for y in range(WALL_TILE, SCREEN_HEIGHT - WALL_TILE, WALL_TILE):
            rock = arcade.SpriteSolidColor(WALL_TILE, WALL_TILE, arcade.color.DARK_BROWN)
            rock.is_rock = False
            rock.is_wall = True
            rock.center_x = WALL_TILE // 2
            rock.center_y = y + WALL_TILE // 2
            self.wall_sprites.append(rock)
            
            rock2 = arcade.SpriteSolidColor(WALL_TILE, WALL_TILE, arcade.color.DARK_BROWN)
            rock2.is_rock = False
            rock2.is_wall = True
            rock2.center_x = SCREEN_WIDTH - WALL_TILE // 2
            rock2.center_y = y + WALL_TILE // 2
            self.wall_sprites.append(rock2)

        def is_position_allowed(x, y, forbidden):
            for fx, fy, r in forbidden:
                if abs(x - fx) < r and abs(y - fy) < r:
                    return False
            return True

        attempts = 0
        spawned = 0
        if room.type not in (RoomType.BOSS, RoomType.START, RoomType.TREASURE):
            while spawned < 6 and attempts < 10:
                attempts += 1
                x = random.randint(180, SCREEN_WIDTH - 180)
                y = random.randint(180, SCREEN_HEIGHT - 180)

                if not is_position_allowed(x, y, room.forbidden_zones):
                    continue

                try:
                    rock = arcade.Sprite("assets/rock.png", scale=6.0)
                except:
                    rock = arcade.SpriteSolidColor(50, 50, arcade.color.BROWN)
                rock.center_x = x
                rock.center_y = y
                rock.is_rock = True        
                rock.is_wall = False
                self.wall_sprites.append(rock)
                spawned += 1

        margin = 80

        def spawn_door(x, y, direction):
            try:
                d = arcade.Sprite("assets/door.png", scale=6.0)
            except Exception:
                d = arcade.SpriteSolidColor(120, 160, arcade.color.DARK_BROWN)
            d.center_x = x
            d.center_y = y
            d.direction = direction
            self.door_sprites.append(d)

        if room.doors.get("up") is not None:
            spawn_door(SCREEN_WIDTH // 2, SCREEN_HEIGHT - margin, "up")
        if room.doors.get("down") is not None:
            spawn_door(SCREEN_WIDTH // 2, margin, "down")
        if room.doors.get("left") is not None:
            spawn_door(margin, SCREEN_HEIGHT // 2, "left")
        if room.doors.get("right") is not None:
            spawn_door(SCREEN_WIDTH - margin, SCREEN_HEIGHT // 2, "right")

        if room.type == RoomType.BOSS:
            bx = SCREEN_WIDTH // 2
            by = SCREEN_HEIGHT // 2 + 60

            if self.floor_number == 1:
                boss = Boss(bx, by)
            elif self.floor_number == 2:
                boss = BossFloor2(bx, by)
            elif self.floor_number == 3:
                boss = BossFloor3(bx, by)

            self.current_enemies.append(boss)
            self.enemy_sprites.append(boss.sprite)
        elif room.type not in (RoomType.WEAPON, RoomType.SHIELD):
            for spawn in room.enemy_spawns:
                x, y = self.find_free_position()
                roll = random.random()
                
                if self.floor_number == 1:
                    if roll < 0.5:
                        e = Enemy(x, y)
                    elif roll < 0.7:
                        e = FastEnemy(x, y)
                    elif roll < 0.9:
                        e = TankEnemy(x, y)
                    else:
                        e = RangedEnemy(x, y)
                
                elif self.floor_number == 2:
                    if roll < 0.35:
                        e = EliteRunner(x, y)
                    elif roll < 0.65:
                        e = EliteShooter(x, y)
                    elif roll < 0.85:
                        e = FastEnemy(x, y)
                    else:
                        e = Enemy(x, y)

                elif self.floor_number == 3:
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

        if room.type == RoomType.TREASURE and room.treasure_unlocked:
            ax = arcade.SpriteSolidColor(28, 28, arcade.color.DARK_ORANGE)
            ax.center_x, ax.center_y = self.find_free_position()
            ax.pickup_type = "axe"
            self.pickup_sprites.append(ax)

            bw = arcade.SpriteSolidColor(28, 28, arcade.color.DARK_GREEN)
            bw.center_x, bw.center_y = self.find_free_position()
            bw.pickup_type = "bow"
            self.pickup_sprites.append(bw)

            if self.floor_number >= 2:
                shield = arcade.SpriteSolidColor(28, 28, arcade.color.BLUE)
                shield.center_x, shield.center_y = self.find_free_position()
                shield.pickup_type = "shield"
                self.pickup_sprites.append(shield)

                halberd = arcade.SpriteSolidColor(32, 32, arcade.color.LIGHT_BLUE)
                halberd.center_x, halberd.center_y = self.find_free_position()
                halberd.pickup_type = "halberd"
                self.pickup_sprites.append(halberd)

                if random.random() > 0.8:
                    hm = arcade.SpriteSolidColor(32, 32, arcade.color.GRAY)
                    hm.center_x, hm.center_y = self.find_free_position()
                    hm.pickup_type = "hammer"
                    self.pickup_sprites.append(hm)

        self.room_cleared = len(self.current_enemies) == 0
        self.player.sprite.center_x = SCREEN_WIDTH // 2
        self.player.sprite.center_y = 190
        
        p = self.player
        if p.has_shield and not p.shield_ready:
            p.shield_room_cooldown -= 1
            if p.shield_room_cooldown <= 0:
                p.shield_ready = True

    def find_free_position(self, min_x=150, max_x=None, min_y=150, max_y=None, tries=100):
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

            if not arcade.check_for_collision_with_list(dummy, self.wall_sprites) and \
               not arcade.check_for_collision_with_list(dummy, self.door_sprites) and \
               not arcade.check_for_collision_with_list(dummy, self.pickup_sprites):
                return x, y

        return SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

    def _update_doors_state(self):
        for door in self.door_sprites:
            door.is_open = self.room_cleared or self.floor.get_current_room().type == RoomType.START
            if isinstance(door, arcade.SpriteSolidColor):
                if door.is_open:
                    door.color = arcade.color.LIGHT_GREEN
                else:
                    door.color = arcade.color.DARK_BROWN

    def on_draw(self):
        self.clear()
        
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
        
        for s in self.sword_slashes:
            arcade.draw_line(s["x1"], s["y1"], s["x2"], s["y2"], arcade.color.WHITE, s["width"])
        
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

        tutorial_button_x = SCREEN_WIDTH - 80
        tutorial_button_y = SCREEN_HEIGHT - 25
        
        arcade.draw_circle_filled(tutorial_button_x, tutorial_button_y, 16, (87, 76, 41))
        arcade.draw_circle_outline(tutorial_button_x, tutorial_button_y, 16, BUTTON_BORDER, 1)
        arcade.draw_text("?", tutorial_button_x, tutorial_button_y, 
                        TEXT_COLOR, 20, anchor_x="center", anchor_y="center",
                        font_name=("Arial", "arial"), bold=True)
        
        arcade.draw_text("F1", tutorial_button_x, tutorial_button_y - 30,
                        arcade.color.LIGHT_GRAY, 14, anchor_x="center", anchor_y="center",
                        font_name=("Arial", "arial"))

        room = self.floor.get_current_room()
        room_type_text = ""
        if room.type == RoomType.START:
            room_type_text = "СТАРТ"
        elif room.type == RoomType.BOSS:
            room_type_text = "БОСС"
        elif room.type == RoomType.TREASURE:
            room_type_text = "СОКРОВИЩНИЦА"
        elif room.type == RoomType.WEAPON:
            room_type_text = "ОРУЖЕЙНАЯ"
            if room.guaranteed_item:
                room_type_text += f" ({room.guaranteed_item.upper()})"
        elif room.type == RoomType.SHIELD:
            room_type_text = "ЩИТОВАЯ"
        else:
            room_type_text = f"КОМНАТА {self.floor.current_pos[0] + 1}-{self.floor.current_pos[1] + 1}"
        
        arcade.draw_text(f"HP: {int(self.player.hp)}/{self.player.max_hp}", 15, SCREEN_HEIGHT - 30, 
                       arcade.color.BLACK, 22)
        arcade.draw_text(f"Keys: {self.player.keys}", 15, SCREEN_HEIGHT - 60,
                       arcade.color.GOLD, 18)
        arcade.draw_text(f"Weapon: {self.player.weapon}", 15, SCREEN_HEIGHT - 90,
                       arcade.color.LIGHT_GRAY, 18)
        
        heart_spacing = 32
        for i in range(self.lives):
            matrix_w = len(HEART_MATRIX[0]) * PIXEL
            matrix_h = len(HEART_MATRIX) * PIXEL
            x = 20 + matrix_w // 2 + i * heart_spacing
            y = SCREEN_HEIGHT - 130 - matrix_h // 2
            top_left_x = x - matrix_w // 2
            top_left_y = y + matrix_h // 2
            draw_pixel_matrix(HEART_MATRIX, top_left_x, top_left_y, arcade.color.RED)
        
        arcade.draw_text(room_type_text, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60,
                       arcade.color.WHITE, 20, anchor_x="center")
        
        arcade.draw_text(f"Этаж {self.floor_number}", SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30,
                       arcade.color.BLACK, 24, anchor_x="center", bold=True)

        if any(isinstance(e, Boss) for e in self.current_enemies):
            boss = next(e for e in self.current_enemies if isinstance(e, Boss))
            bar_w = 450
            x = (SCREEN_WIDTH - bar_w) // 2
            y = SCREEN_HEIGHT - 60
            ratio = max(0.0, boss.hp / boss.max_hp)
            arcade.draw_lbwh_rectangle_filled(x, y - 7, int(bar_w * ratio), 14, arcade.color.RED)
            arcade.draw_lrbt_rectangle_outline(x, x + bar_w, y - 7, y + 7, arcade.color.WHITE)
            
            arcade.draw_text(f"Фаза: {boss.phase}", x + bar_w // 2, y - 30,
                           arcade.color.YELLOW, 16, anchor_x="center")
        
        if self.room_cleared and self.floor.get_current_room().type != RoomType.BOSS:
            arcade.draw_text("E - войти в дверь", SCREEN_WIDTH // 2, 40,
                           arcade.color.LIGHT_GREEN, 18, anchor_x="center")
        
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

        if self.notice_timer > 0 and self.notice_text:
            arcade.draw_text(self.notice_text, SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT - 100, arcade.color.YELLOW, 20)

    def on_update(self, dt):
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

        if dx or dy:
            length = math.hypot(dx, dy)
            nx = dx / length
            ny = dy / length

            old_x = self.player.sprite.center_x
            self.player.sprite.center_x += nx * self.player.speed * dt
            if arcade.check_for_collision_with_list(self.player.sprite, self.wall_sprites):
                self.player.sprite.center_x = old_x

            old_y = self.player.sprite.center_y
            self.player.sprite.center_y += ny * self.player.speed * dt
            if arcade.check_for_collision_with_list(self.player.sprite, self.wall_sprites):
                self.player.sprite.center_y = old_y

            if nx > 0:
                self.player.sprite.scale_x = abs(self.player.sprite.scale_x)
            elif nx < 0:
                self.player.sprite.scale_x = -abs(self.player.sprite.scale_x)

        self.player.update(dt, self.keys_held)
        p = self.player
        room = self.floor.get_current_room()

        if p.has_shield and not p.shield_ready:
            if room.type == RoomType.BOSS:
                p.shield_time_cooldown -= dt
                if p.shield_time_cooldown <= 0:
                    p.shield_ready = True

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
                    enemies=new_enemies,
                    enemy_projectiles=self.projectile_sprites
                )
                if len(new_enemies) > 0:
                    for ne in new_enemies:
                        self.current_enemies.append(ne)
                        self.enemy_sprites.append(ne.sprite)
                    new_enemies.clear()
            elif isinstance(e, (RangedEnemy, EliteShooter, EliteArcherFloor3)):
                e.update(self.player, self.wall_sprites, dt, self.projectile_sprites)
            else:
                e.update(self.player, self.wall_sprites, dt)
            
            if abs(e.x - self.player.x) < 28 and abs(e.y - self.player.y) < 28:
                self.player.hp -= 20 * dt

            if not e.alive:
                try:
                    self.current_enemies.remove(e)
                except ValueError:
                    pass
                try:
                    self.enemy_sprites.remove(e.sprite)
                except ValueError:
                    pass

        for proj in list(self.projectile_sprites):
            proj.center_x += proj.change_x * dt
            proj.center_y += proj.change_y * dt

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

            if arcade.check_for_collision_with_list(proj, self.wall_sprites):
                try:
                    self.projectile_sprites.remove(proj)
                except ValueError:
                    pass
                continue
            
            if proj.center_x < -200 or proj.center_x > SCREEN_WIDTH + 200 or proj.center_y < -200 or proj.center_y > SCREEN_HEIGHT + 200:
                try:
                    self.projectile_sprites.remove(proj)
                except ValueError:
                    pass

        for s in list(self.sword_slashes):
            s["time"] -= dt
            if s["time"] <= 0:
                self.sword_slashes.remove(s)

        for a in list(self.axe_swings):
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

                    enemy_angle = math.degrees(math.atan2(dx, dy))
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
                h["phase"] = "impact"

                for e in self.current_enemies:
                    if arcade.get_distance_between_sprites(e.sprite, self.player.sprite) <= h["radius"]:
                        e.hp -= h["damage"]
                        
                        if getattr(e, "can_be_stunned", True):                         
                            e.stunned = True
                            e.stun_timer = HAMMER_STUN_TIME
                        else:
                            e.slowed = True
                            e.slow_timer = HAMMER_BOSS_SLOW_TIME
                            e.slow_mult = HAMMER_BOSS_SLOW_MULT

                for obj in self.wall_sprites[:]:
                    if not getattr(obj, "is_rock", False):
                        continue

                    if arcade.get_distance_between_sprites(obj, self.player.sprite) <= h["radius"]:
                        obj.remove_from_sprite_lists()
            
            if h["timer"] <= 0:
                self.hammer_swings.remove(h)

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
                elif ptype == "heart":
                    self.player.max_hp += 20
                    self.player.hp = min(self.player.max_hp, self.player.hp + 40)
                    self.notice_text = "Max HP increased!"
                    self.notice_timer = 2.0
                
                try:
                    self.pickup_sprites.remove(p)
                except ValueError:
                    pass

        prev_cleared = self.room_cleared
        self.room_cleared = len(self.current_enemies) == 0
        room = self.floor.get_current_room()

        if self.room_cleared and room.type == RoomType.BOSS:
            completed_levels[self.floor_number] = True
            
            self.notice_text = f"УРОВЕНЬ {self.floor_number} ПРОЙДЕН!"
            self.notice_timer = 3.0
            
            if self.floor_number == 3 and all(completed_levels.values()):
                time.sleep(1.0)
                good_ending_view = GoodEndingView()
                good_ending_view.setup()
                self.window.show_view(good_ending_view)
            else:
                if self.notice_timer <= 0:
                    floor_view = FloorSelectionView()
                    floor_view.setup()
                    self.window.show_view(floor_view)

        if self.room_cleared and (not prev_cleared):
            if room.type not in (RoomType.START, RoomType.BOSS, RoomType.TREASURE, RoomType.WEAPON, RoomType.SHIELD):
                if random.random() < KEY_DROP_CHANCE:
                    kx, ky = self.find_free_position()
                    key_sprite = arcade.SpriteSolidColor(24, 18, arcade.color.GOLD)
                    key_sprite.center_x = kx
                    key_sprite.center_y = ky
                    key_sprite.pickup_type = "key"
                    self.pickup_sprites.append(key_sprite)
                    self.notice_text = "A key dropped!"
                    self.notice_timer = 2.0

        if self.notice_timer > 0:
            self.notice_timer -= dt
            if self.notice_timer <= 0:
                self.notice_text = ""

        if self.player.hp <= 0:
            self.lives -= 1
            
            if self.lives > 0:
                self.player.hp = self.player.max_hp
                self.load_current_room()
            else:
                bad_ending_view = BadEndingView(self.floor_number)
                bad_ending_view.setup()
                self.window.show_view(bad_ending_view)

    def on_key_press(self, key, modifiers):
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

        if key in (arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT):
            if self.player.weapon == "axe":
                if not self.player.can_attack():
                    return
                self.player.reset_attack()
                swing = {"x": self.player.x, "y": self.player.y, "radius": 120, "time": 0.18, "damage": 70, "applied": False}
                self.axe_swings.append(swing)
            
            elif self.player.weapon == "halberd":
                if not self.player.can_attack():
                    return

                self.player.attack_cooldown = HALBERD_COOLDOWN
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
                    "angle": angle,
                    "radius": HALBERD_RADIUS,
                    "arc": HALBERD_ARC_ANGLE,
                    "time": HALBERD_TIME,
                    "damage": HALBERD_DAMAGE,
                    "applied": False
                }

                self.halberd_swings.append(swing)
                return
            
            elif self.player.weapon == "hammer":
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
                
                try:
                    arrow = arcade.Sprite("assets/arrow.png", scale=5)
                except:
                    arrow = arcade.SpriteSolidColor(10, 10, arcade.color.YELLOW)

                arrow.center_x = self.player.x
                arrow.center_y = self.player.y
                
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

                self.sword_slashes.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2, "time": SWORD_TIME, "width": SWORD_THICKNESS})

                for e in list(self.current_enemies):
                    if abs(e.x - x2) < 48 and abs(e.y - y2) < 48:
                        e.hp -= 40

        if key == arcade.key.E and self.room_cleared:
            room = self.floor.get_current_room()
            for door in list(self.door_sprites):
                if arcade.check_for_collision(self.player.sprite, door):
                    target = self.floor.get_current_room().doors.get(door.direction)
                    if not target:
                        continue
                    target_room = self.floor.rooms.get(target)
                    
                    if target_room and target_room.type == RoomType.TREASURE and (not target_room.treasure_unlocked):
                        if self.player.keys > 0:
                            self.player.keys -= 1
                            target_room.treasure_unlocked = True
                            self.notice_text = "Unlocked treasure room!"
                            self.notice_timer = 2.0
                            if self.floor.move(target):
                                self.load_current_room()
                        else:
                            self.notice_text = "Door is locked. Need a key."
                            self.notice_timer = 2.0
                        break
                    else:
                        if self.floor.move(target):
                            self.load_current_room()
                        break

        if key == arcade.key.F1:
            tutorial_view = TutorialView(self)
            tutorial_view.setup()
            self.window.show_view(tutorial_view)

        if key == arcade.key.ESCAPE:
            floor_view = FloorSelectionView()
            floor_view.setup()
            self.window.show_view(floor_view)

        if key == arcade.key.R:
            self.floor = Floor(self.floor_number)
            self.load_current_room()
    
    def on_mouse_press(self, x, y, button, modifiers):
        tutorial_button_x = SCREEN_WIDTH - 80
        tutorial_button_y = SCREEN_HEIGHT - 25
        dist = math.sqrt((x - tutorial_button_x) ** 2 + (y - tutorial_button_y) ** 2)
        
        if dist <= 16:
            tutorial_view = TutorialView(self)
            tutorial_view.setup()
            self.window.show_view(tutorial_view)
    
    def on_key_release(self, key, modifiers):
        self.keys_held.discard(key)

class GoodEndingView(arcade.View):
    def __init__(self):
        super().__init__()
        self.button_list = []
        self.hovered_button = None
        self.pressed_button = None
        
    def setup(self):
        back_button = {
            "x": SCREEN_WIDTH // 2 - 120,
            "y": 80,
            "width": 240,
            "height": 50,
            "text": "В ГЛАВНОЕ МЕНЮ",
            "action": "back"
        }
        self.button_list.append(back_button)
        
    def on_draw(self):
        self.clear()
        
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                SCREEN_WIDTH // 2, 
                SCREEN_HEIGHT // 2, 
                SCREEN_WIDTH, 
                SCREEN_HEIGHT
            ),
            (0, 0, 0)
        )
        
        ending_text_lines = [
            "ХОРОШАЯ КОНЦОВКА",
            "",
            "Вы прошли все три уровня Падшего Замка.",
            "Победив последнего босса, вы наконец",
            "обрели покой и завершили свою историю.",
            "",
            "Тысячелетний сон окончен,",
            "и теперь вы свободны от прошлого.",
            "Память вернулась, и с ней пришло понимание:",
            "иногда искупление требует больше сил,",
            "чем сама битва.",
            "",
            "Замок наконец обрел покой,",
            "а вместе с ним и вы."
        ]
        
        y_pos = SCREEN_HEIGHT // 2 + 140
        for i, line in enumerate(ending_text_lines):
            color = (255, 255, 255)
            font_size = 18
            if line.startswith("ХОРОШАЯ КОНЦОВКА"):
                color = (255, 215, 0)
                font_size = 36
                y_pos -= 40
            
            if line:
                arcade.draw_text(
                    line,
                    SCREEN_WIDTH // 2,
                    y_pos - i * 25,
                    color,
                    font_size,
                    anchor_x="center",
                    anchor_y="center",
                    font_name=("Arial", "arial"),
                    bold=(line.startswith("ХОРОШАЯ КОНЦОВКА"))
                )
        
        for button in self.button_list:
            if self.pressed_button == button:
                color = BUTTON_PRESSED
            elif self.hovered_button == button:
                color = BUTTON_HOVER
            else:
                color = BUTTON_NORMAL
            
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    button["x"] + button["width"] // 2,
                    button["y"] + button["height"] // 2,
                    button["width"],
                    button["height"]
                ),
                color
            )
            
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
                    
                    if btn["action"] == "back":
                        global completed_levels
                        completed_levels = {1: False, 2: False, 3: False}
                        menu_view = MainMenuView()
                        menu_view.setup()
                        self.window.show_view(menu_view)
                    
                    break
        
        self.pressed_button = None
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER or key == arcade.key.SPACE or key == arcade.key.ESCAPE:
            global completed_levels
            completed_levels = {1: False, 2: False, 3: False}
            menu_view = MainMenuView()
            menu_view.setup()
            self.window.show_view(menu_view)

class BadEndingView(arcade.View):
    def __init__(self, floor_number):
        super().__init__()
        self.floor_number = floor_number
        self.button_list = []
        self.hovered_button = None
        self.pressed_button = None
        
    def setup(self):
        back_button = {
            "x": SCREEN_WIDTH // 2 - 120,
            "y": 80,
            "width": 240,
            "height": 50,
            "text": "В ГЛАВНОЕ МЕНЮ",
            "action": "back"
        }
        self.button_list.append(back_button)
        
    def on_draw(self):
        self.clear()
        
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                SCREEN_WIDTH // 2, 
                SCREEN_HEIGHT // 2, 
                SCREEN_WIDTH, 
                SCREEN_HEIGHT
            ),
            (0, 0, 0)
        )
        
        floor_names = {
            1: "КРЕПОСТНОЙ СТЕНЕ",
            2: "ЦИТАДЕЛИ",
            3: "ПОДЗЕМЕЛЬЕ"
        }
        
        ending_text_lines = [
            "ПЛОХАЯ КОНЦОВКА",
            "",
            f"Вы пали на {floor_names.get(self.floor_number, 'этом уровне')}.",
            "Ваши силы иссякли, и тьма поглотила вас.",
            "",
            "Тысячелетний сон продолжится,",
            "но на этот раз — навсегда.",
            "",
            "Замок Падших обрел новую жертву,",
            "и его стены будут хранить вашу память",
            "как предупреждение для следующих смельчаков.",
            "",
            "Иногда битва оказывается сильнее воина..."
        ]
        
        y_pos = SCREEN_HEIGHT // 2 + 140
        for i, line in enumerate(ending_text_lines):
            color = (255, 255, 255)
            font_size = 18
            if line.startswith("ПЛОХАЯ КОНЦОВКА"):
                color = (255, 100, 100)
                font_size = 36
                y_pos -= 40
            
            if line:
                arcade.draw_text(
                    line,
                    SCREEN_WIDTH // 2,
                    y_pos - i * 25,
                    color,
                    font_size,
                    anchor_x="center",
                    anchor_y="center",
                    font_name=("Arial", "arial"),
                    bold=(line.startswith("ПЛОХАЯ КОНЦОВКА"))
                )
        
        for button in self.button_list:
            if self.pressed_button == button:
                color = BUTTON_PRESSED
            elif self.hovered_button == button:
                color = BUTTON_HOVER
            else:
                color = BUTTON_NORMAL
            
            arcade.draw_rect_filled(
                arcade.rect.XYWH(
                    button["x"] + button["width"] // 2,
                    button["y"] + button["height"] // 2,
                    button["width"],
                    button["height"]
                ),
                color
            )
            
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
                    
                    if btn["action"] == "back":
                        global completed_levels
                        completed_levels = {1: False, 2: False, 3: False}
                        menu_view = MainMenuView()
                        menu_view.setup()
                        self.window.show_view(menu_view)
                    
                    break
        
        self.pressed_button = None
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER or key == arcade.key.SPACE or key == arcade.key.ESCAPE:
            global completed_levels
            completed_levels = {1: False, 2: False, 3: False}
            menu_view = MainMenuView()
            menu_view.setup()
            self.window.show_view(menu_view)

