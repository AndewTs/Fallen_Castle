import arcade
from src.settings import *
from src.game_view import MainMenuView


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=False)
        arcade.set_background_color((0, 0, 0))
    
    def setup(self):
        menu_view = MainMenuView()
        menu_view.setup()
        self.show_view(menu_view)