"""
 Keyboard Keys  Mapped To  Chi8 Keys
 -------------            ---------
 1 2 3 4                   1 2 3 C
 q w e r                   4 5 6 D
 a s d f                   7 8 9 E
 z x c v                   A 0 B F
"""

my_keyboard_keys = [
    '1', '2', '3', '4',
    'q', 'w', 'e', 'r',
    'a', 's', 'd', 'f',
    'z', 'x', 'c', 'v',
]

chip8_keys = [
    1, 2, 3, 0xC,
    4, 5, 6, 0xD,
    7, 8, 9, 0xE,
    0xA, 0, 0xB, 0xF,
]

key_dict = {}

for i in range(len(chip8_keys)):
    key_dict[ord(my_keyboard_keys[i])] = chip8_keys[i]
