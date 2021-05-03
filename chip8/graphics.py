import os

import pygame
import chip8.constants as constants


class Screen:
    HEIGHT = 32
    WIDTH = 64

    def __init__(self):
        self.scale = constants.SCREEN_SCALE
        self.pixels = [[0 for i in range(self.WIDTH)] for j in range(self.HEIGHT)]

        self.background_color = constants.BACKGROUND_COLOR
        self.active_color = constants.ACTIVE_COLOR

        self.screen_width = self.WIDTH * self.scale
        self.screen_height = self.HEIGHT * self.scale

        self.beep_sound = None
        self.display = None

    def initialize(self):
        pygame.init()

        # The mixer used for sounds
        pygame.mixer.init()

        sound_file_path = os.path.join(os.path.dirname(__file__), 'sound/beep.wav')
        self.beep_sound = pygame.mixer.Sound(sound_file_path)

        self.display = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.display.fill(self.background_color)

    def update_screen(self):
        for col in range(self.HEIGHT):
            for row in range(self.WIDTH):
                bit = self.pixels[col][row]
                color = None
                if bit == 1:
                    color = self.active_color
                else:
                    color = self.background_color

                self.draw_pixel(row, col, color=color)
        pygame.display.flip()

    def draw_pixel(self, x, y, color=None):
        if color is None:
            color = self.active_color
        # Making sure pixels not out of range
        assert_condition = ((0 <= x <= 63) and (0 <= y <= 31))
        assert assert_condition, "Pixels out of range"

        block_size = self.scale - self.scale/10000
        pygame.draw.rect(self.display, color, (x * self.scale, y * self.scale, block_size, block_size))

    def draw_sprite(self, sprite, x, y):

        n = len(sprite)
        collision = 0
        for j in range(n):
            byte = sprite[j]
            byte_string = '{0:08b}'.format(byte)
            offset_y = y + j
            offset_x = x
            for i in range(8):
                pixel = int(byte_string[i])
                location_x = (offset_x + i) % self.WIDTH
                location_y = offset_y % self.HEIGHT
                old_pixel = self.pixels[location_y][location_x]
                new_pixel = pixel ^ old_pixel
                self.pixels[location_y][location_x] = new_pixel
                if pixel == 1 and old_pixel == 1:
                    collision = 1
        return collision

    def clear_screen(self):
        for i in range(self.HEIGHT):
            for j in range(self.WIDTH):
                self.pixels[i][j] = 0

    def play_beep_sound(self):
        self.beep_sound.play()
