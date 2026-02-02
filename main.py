# main.py
import arcade
from src.window import GameWindow


def main():
    window = GameWindow()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
