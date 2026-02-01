import arcade
from src.settings import PLAYER_HP, PLAYER_SCALE, PLAYER_SPEED


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