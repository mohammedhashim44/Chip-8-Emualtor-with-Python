import pygame
import random

from chip8.decoder import Decoder, OpCodes
from chip8.graphics import Screen

import chip8.constants as constants
import chip8.fonts as Fonts
import chip8.keys as Keys


class Chip8:
    def __init__(self):
        # 4096 BYTES
        self.memory = [0] * 4096

        # 16 8-bit registers
        self.V = [0] * 16

        # 2 special registers , 8-bit each
        # PC start at location 0x200
        self.I = 0
        self.PC = 0x200

        # 64 x 32 pixels
        self.pixels = [64 * 32] * 0

        # 2 8-bit timers
        self.delay_timer = 0
        self.sound_timer = 0

        # Stack and stack pointer
        self.stack = [0] * 16
        self.stack_pointer = -1

        # Initialize op code
        self.op_code = 0
        self.decoded_instruction = None

        self.decoder = None
        self.screen = None
        self.keys = None

    def initialize(self):
        # Initialize decoder
        self.decoder = Decoder()

        # Initialize Screen
        self.screen = Screen()
        self.screen.initialize()

        self.load_fonts()
        self.setup_keys()

    def load_fonts(self):
        # Fonts loaded from 0 to 80
        for i in range(len(Fonts.fonts)):
            self.memory[i] = Fonts.fonts[i]

    def setup_keys(self):
        self.keys = []
        for i in range(16):
            self.keys.append(False)

    def load_game(self, game_path):
        buffer = []
        chunk_size = 1
        with open(game_path, "rb") as f:
            bytes_read = f.read(chunk_size)
            buffer.append(bytes_read)
            while bytes_read:
                bytes_read = f.read(chunk_size)
                if bytes_read is not None and bytes_read != b'':
                    buffer.append(bytes_read)

        # Save buffer to memory
        for i in range(0, len(buffer)):
            hex_of_buffer = buffer[i].hex()
            int_of_opcode = int(hex_of_buffer, base=16)
            self.memory[512 + i] = int_of_opcode

    def loop(self):
        clock = pygame.time.Clock()
        clock_speed = constants.CLOCK_SPEED
        while True:
            # -> Keys
            # -> Fetch OpCode
            # -> Decode OpCode and get Instruction
            # -> Execute Instruction
            # -> Update screen
            # -> Update program counter
            # -> Update timers

            clock.tick(clock_speed)
            self.handle_keys()
            self.fetch_opcode()
            self.decode_opcode()
            self.execute_instruction()
            self.screen.update_screen()
            self.increment_counter()
            self.update_timers()

    def update_timers(self):
        if self.delay_timer >= 1:
            self.delay_timer = self.delay_timer - 1

        # Play beep sound if timer hit 0
        if self.sound_timer >= 1:
            self.sound_timer = self.sound_timer - 1
            if self.sound_timer == 0:
                self.screen.play_beep_sound()

    def handle_keys(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                pressed_key = event.key
                if pressed_key in Keys.key_dict:
                    mapped_key = Keys.key_dict[pressed_key]
                    msg = fr"Yuo Pressed : {chr(pressed_key)}"
                    self.debug_print(msg)
                    self.keys[mapped_key] = True
            elif event.type == pygame.KEYUP:
                released_key = event.key
                if released_key in Keys.key_dict:
                    mapped_key = Keys.key_dict[released_key]
                    msg = fr"You Released : {chr(released_key)}"
                    self.debug_print(msg)
                    self.keys[mapped_key] = False

    def fetch_opcode(self):
        # Opcode is 2 Byte long
        first_half = self.memory[self.PC]
        second_half = self.memory[self.PC + 1]
        op_code = (first_half << 8) + second_half
        self.op_code = op_code

    def decode_opcode(self):
        op_code = self.op_code
        decoded_instruction = self.decoder.decode(op_code)
        if decoded_instruction == OpCodes._NO_OPCODE:
            print("Unexpected Error Happened")
            exit()
        self.decoded_instruction = decoded_instruction

    def get_arguments(self, op_code):
        # _xy_
        # __kk
        # _nnn
        # ___n

        x = (op_code & 0x0F00) >> 8
        y = (op_code & 0x00F0) >> 4
        kk = (op_code & 0x00FF)
        nnn = (op_code & 0x0FFF)
        n = (op_code & 0x000F)
        return x, y, kk, nnn, n

    def increment_counter(self):
        self.PC = self.PC + 2

    def execute_instruction(self):
        op_code = self.op_code
        instruction = self.decoded_instruction
        x, y, kk, nnn, n = self.get_arguments(op_code)
        op_code_hex = self.format_to_hex(op_code)[2:]

        if instruction == OpCodes._00E0_CLS:
            msg = "00e0 : Clearing Screen"
            self.debug_print(msg)

            self.screen.clear_screen()

        elif instruction == OpCodes._00E0_RET:
            # Return from subroutine
            msg = fr"{op_code_hex} : Return From Subroutine"
            self.debug_print(msg)

            self.PC = self.stack[self.stack_pointer]
            self.stack_pointer = self.stack_pointer - 1

        elif instruction == OpCodes._1NNN_JP_ADDR:
            # sets the program counter to nnn.
            msg = fr"{op_code_hex} : Set PC to nnn"
            self.debug_print(msg)

            self.PC = nnn - 2

        elif instruction == OpCodes._2NNN_CALL_ADDR:
            # Call Subroutine nnn
            msg = fr"{op_code_hex} : Call subroutine at nnn"
            self.debug_print(msg)

            self.stack_pointer = self.stack_pointer + 1
            self.stack[self.stack_pointer] = self.PC
            self.PC = nnn - 2
        elif instruction == OpCodes._3XKK_SE_VX_BYTE:
            # Skip next instruction if V[x] == KK
            msg = fr"{op_code_hex} : Skip next instruction if V[x] == KK"
            self.debug_print(msg)

            if self.V[x] == kk:
                self.increment_counter()

        elif instruction == OpCodes._4XKK_SNE_VX_BYTE:
            # Skip next instruction if V[x] != KK
            msg = fr"{op_code_hex} : Skip next instruction if Vx != kk"
            self.debug_print(msg)

            if self.V[x] != kk:
                self.increment_counter()

        elif instruction == OpCodes._5XY0_SE_VX_VY:
            # Skip next instruction if v[x] == v[y]
            msg = fr"{op_code_hex} : Skip next instruction if Vx == Vy"
            self.debug_print(msg)

            if self.V[x] == self.V[y]:
                self.increment_counter()

        elif instruction == OpCodes._6XKK_LD_VX_BYTE:
            # Put value kk in V[x]
            msg = fr"{op_code_hex} : Put value kk in Vx"
            self.debug_print(msg)

            self.V[x] = kk

        elif instruction == OpCodes._7XKK_ADD_VX_BYTE:
            # Vx = Vx + kk
            msg = fr"{op_code_hex} : Set Vx = Vx + kk"
            self.debug_print(msg)

            ans, carry = self.add(self.V[x], kk)
            self.V[x] = ans

        elif instruction == OpCodes._8XY0_LD_VX_VY:
            # Set Vx = Vy.
            msg = fr"{op_code_hex} : Set Vx = Vy"
            self.debug_print(msg)

            self.V[x] = self.V[y]

        elif instruction == OpCodes._8XY1_OR_VX_VY:
            # Set Vx = Vx OR Vy
            msg = fr"{op_code_hex} : Set Vx = Vx OR Vy"
            self.debug_print(msg)

            self.V[x] = self.V[x] | self.V[y]

        elif instruction == OpCodes._8XY2_AND_VX_VY:
            # Set Vx = Vx AND Vy
            msg = fr"{op_code_hex} : Set Vx = Vx AND Vy"
            self.debug_print(msg)

            self.V[x] = self.V[x] & self.V[y]

        elif instruction == OpCodes._8XY3_XOR_VX_VY:
            # Set Vx = Vx XOR Vy
            msg = fr"{op_code_hex} : Set Vx = Vx XOR Vy"
            self.debug_print(msg)

            self.V[x] = self.V[x] ^ self.V[y]

        elif instruction == OpCodes._8XY4_ADD_VX_VY:
            # Set Vx = Vx + Vy, set VF = carry.
            msg = fr"{op_code_hex} : Set Vx = Vx + Vy, set VF = carry"
            self.debug_print(msg)

            ans, carry = self.add(self.V[x], self.V[y])
            self.V[x] = ans
            self.V[0xF] = 1 if carry else 0

        elif instruction == OpCodes._8xy5_SUB_VX_VY:
            # Set Vx = Vx - Vy, set VF = NOT borrow
            msg = fr"{op_code_hex} : Set Vx = Vx - Vy, set VF = NOT borrow"
            self.debug_print(msg)

            ans, carry = self.sub(self.V[x], self.V[y])
            self.V[0xF] = 0 if carry else 1
            self.V[x] = ans

        elif instruction == OpCodes._8XY6_SHR_VX:
            # Set Vx = Vx SHR 1, set VF = Overflow
            msg = fr"{op_code_hex} : Set Vx = Vx SHR 1, set VF = Overflow"
            self.debug_print(msg)

            lower_digit_is_one = ((self.V[x] & 1) == 1)
            ans = self.V[x] >> 1

            self.V[x] = ans
            self.V[0xF] = lower_digit_is_one

        elif instruction == OpCodes._8XY7_SUBN_VX_VY:
            # Set Vx = Vy - Vx, set VF = NOT borrow
            msg = fr"{op_code_hex} : Set Vx = Vy - Vx, set VF = NOT borrow"
            self.debug_print(msg)

            ans, carry = self.sub(self.V[y], self.V[x])
            self.V[0xF] = 0 if carry else 1
            self.V[x] = ans

        elif instruction == OpCodes._820E_SHL_VX:
            # Set Vx = Vx SHL 1
            # If the most-significant bit of Vx is 1,
            # then VF is set to 1, otherwise to 0
            msg = fr"{op_code_hex} : Set Vx = Vx SHL 1"
            self.debug_print(msg)

            msb_is_one = ((self.V[x] & 0x80) == 0x80)
            self.V[0xF] = 1 if msb_is_one else 0
            self.V[x] = ((self.V[x] << 1) & 0xFF)

        elif instruction == OpCodes._9XY0_SNE_VX_VY:
            # Skip next instruction if Vx != Vy
            msg = fr"{op_code_hex} : Skip next instruction if Vx != Vy"
            self.debug_print(msg)

            if self.V[x] != self.V[y]:
                self.increment_counter()

        elif instruction == OpCodes._ANNN_LD_I_ADDR:
            # Set IndexRegister to nnn
            msg = fr"{op_code_hex} : Set IndexRegister to nnn"
            self.debug_print(msg)

            self.I = nnn

        elif instruction == OpCodes._BNNN_JP_V0_ADDR:
            # Set PC to nnn + V[0]
            msg = fr"{op_code_hex} : Set PC to nnn + V[0]"
            self.debug_print(msg)

            self.PC = nnn + self.V[0] - 2

        elif instruction == OpCodes._CKKK_RND_VX_BYTE:
            # Vx = Random BYTE & kk
            msg = fr"{op_code_hex} : Set Vx = random byte AND kk"
            self.debug_print(msg)

            random_byte = random.getrandbits(8)
            ans = random_byte & kk
            self.V[x] = ans

        elif instruction == OpCodes._DXYN_DRW_VX_VY:
            # Display n-bytes sprite starting at location I at (Vx,Vy)
            msg = fr"{op_code_hex} : Drawing Sprite"
            self.debug_print(msg)

            sprite = self.memory[self.I: self.I + n]
            location_x = self.V[x]
            location_y = self.V[y]
            collision = self.screen.draw_sprite(sprite, location_x, location_y)
            self.V[0xF] = collision

        elif instruction == OpCodes._E09E_SKP_VX:
            # Skip next instruction if key with the value of Vx is pressed.
            msg = fr"{op_code_hex} : Set next instruction if Vx pressed"
            self.debug_print(msg)

            key = self.V[x]
            self.handle_keys()
            if self.keys[key] == True:
                self.increment_counter()

        elif instruction == OpCodes._EXA1_SKPN_VX:
            # Skip next instruction if key with the value of Vx is not pressed.
            msg = fr"{op_code_hex} : Set next instruction if Vx not pressed"
            self.debug_print(msg)

            key = self.V[x]
            self.handle_keys()
            if self.keys[key] == False:
                self.increment_counter()

        elif instruction == OpCodes._FX07_LD_VX_DT:
            # Set Vx = delay timer value.
            msg = fr"{op_code_hex} : Set Vx = delay timer value"
            self.debug_print(msg)

            self.V[x] = self.delay_timer

        elif instruction == OpCodes._FX0A_LD_VX_K:
            # Wait for a key press, store the value of the key in Vx.
            msg = fr"{op_code_hex} : Wait for a key press, store the value of the key in Vx"
            self.debug_print(msg)

            key = None
            while True:
                self.handle_keys()
                key_down = False
                for i in range(len(self.keys)):
                    if self.keys[i] == True:
                        key = i
                        key_down = True
                if key_down == True:
                    break
            self.V[x] = key

        elif instruction == OpCodes._FX15_LD_DT_VX:
            # Set delay timer = Vx.
            msg = fr"{op_code_hex} : Set delay timer = Vx"
            self.debug_print(msg)

            self.delay_timer = self.V[x]

        elif instruction == OpCodes._FX18_LD_ST_VX:
            # Set sound timer = Vx.
            msg = fr"{op_code_hex} : Set sound timer = Vx"
            self.debug_print(msg)

            self.sound_timer = self.V[x]

        elif instruction == OpCodes._FX1E_ADD_I_VX:
            # Set I = I + Vx.
            msg = fr"{op_code_hex} : Set I = I + Vx"
            self.debug_print(msg)

            # I is 16-bit register
            ans, carry = self.add(self.I, self.V[x], bits=16)
            self.I = ans

        elif instruction == OpCodes._FX29_LD_F_VX:
            # Set I to the memory address of the sprite data corresponding
            # to the hexadecimal digit stored in register VX
            msg = fr"{op_code_hex} : Set I to SPRITE location"
            self.debug_print(msg)

            sprite_digit = self.V[x]
            sprite_location = sprite_digit * 5
            self.I = sprite_location

        elif instruction == OpCodes._FX33_LD_B_VX:
            msg = fr"{op_code_hex} : Store BCD represntation"
            self.debug_print(msg)

            bcd = self.to_bcd(self.V[x])
            for i in range(3):
                self.memory[self.I + i] = bcd[i]

        elif instruction == OpCodes._FX55_LD_I_VX:
            # Store registers V0 through Vx in memory starting at location I.
            msg = fr"{op_code_hex} : Store registers V0 through Vx in memory starting at location I"
            self.debug_print(msg)

            for i in range(x + 1):
                self.memory[self.I + i] = self.V[i]

        elif instruction == OpCodes._FX65_LD_VX_I:
            # Read registers V0 through Vx from memory starting at location I.
            msg = fr"{op_code_hex} : Load registers from memory"
            self.debug_print(msg)

            for i in range(x + 1):
                self.V[i] = self.memory[self.I + i]

    def to_bcd(self, number):
        # 5 6 8
        # Will be =>
        # [ 5 , 6 , 8 ]

        str_number = str(number).zfill(3)
        bcd = []
        for i in str_number:
            bcd.append(int(i))
        return bcd

    def add(self, one, two, bits=8):
        # Number of bits with AND operation
        # to limit the number to 8 bits or 16 bits

        c = one + two
        carry = (c & 0xFF00) > 0
        c = (c & 0xFF) if bits == 8 else (c & 0xFFFF)
        return c, carry

    def sub(self, one, two):
        borrow = two > one
        c = (abs(one - two) & 0xFF)
        return c, borrow


    def format_to_hex(self, number):
        return f"{number:#0{6}x}"

    def debug_print(self, string):
        if constants.DEBUG_PRINT:
            print(string)
