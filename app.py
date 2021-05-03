import sys

from chip8.chip8 import Chip8

if __name__ == "__main__":
    game = sys.argv[1]
    chip8 = Chip8()
    chip8.load_game(game)
    chip8.initialize()
    chip8.loop()
