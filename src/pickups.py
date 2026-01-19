import arcade
from settings import HEART_MATRIX, PIXEL


def draw_pixel_matrix(matrix, x, y, color):
    for r, row in enumerate(matrix):
        for c, cell in enumerate(row):
            if cell == "1":
                left = x + c * PIXEL
                bottom = y - (r + 1) * PIXEL
                arcade.draw_lbwh_rectangle_filled(left, bottom, PIXEL, PIXEL, color)


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