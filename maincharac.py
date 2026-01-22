import arcade
from settings import SCREEN_HEIGHT, SCREEN_WIDTH, PLAYER_SPEED, ATTACK_COOLDOWN
class Player:
    def __init__(self):
        self.sprite = arcade.Sprite("assets/Player 2.png", scale=0.1)

        self.sprite.center_x = SCREEN_WIDTH // 2
        self.sprite.center_y = SCREEN_HEIGHT // 2

        self.speed = PLAYER_SPEED
        self.hp = 100
        self.max_hp = 100

        self.attack_cooldown = ATTACK_COOLDOWN
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
        self.sprite.center_x = max(24, min(SCREEN_WIDTH - 24, self.sprite.center_x))
        self.sprite.center_y = max(24, min(SCREEN_HEIGHT - 24, self.sprite.center_y))

    def update(self, dt):
        if self.attack_timer > 0:
            self.attack_timer -= dt

    def can_attack(self):
        return self.attack_timer <= 0

    def reset_attack(self):
        self.attack_timer = self.attack_cd