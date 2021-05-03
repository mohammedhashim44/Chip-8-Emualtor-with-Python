from enum import Enum


class OpCodes(Enum):
    _NO_OPCODE = None
    _00E0_CLS = "00E0"
    _00E0_RET = "00EE"
    _0NNN_SYS_ADDR = "0nnn"
    _1NNN_JP_ADDR = "1nnn"
    _2NNN_CALL_ADDR = "2nnn"
    _3XKK_SE_VX_BYTE = "3xkk"
    _4XKK_SNE_VX_BYTE = "4xkk"
    _5XY0_SE_VX_VY = "5xy0"
    _6XKK_LD_VX_BYTE = "6xkk"
    _7XKK_ADD_VX_BYTE = "7xkk"
    _8XY0_LD_VX_VY = "8xy0"
    _8XY1_OR_VX_VY = "8xy1"
    _8XY2_AND_VX_VY = "8xy2"
    _8XY3_XOR_VX_VY = "8xy3"
    _8XY4_ADD_VX_VY = "8xy4"
    _8xy5_SUB_VX_VY = "8xy5"
    _8XY6_SHR_VX = "8xy6"
    _8XY7_SUBN_VX_VY = "8xy7"
    _820E_SHL_VX = "8xyE"
    _9XY0_SNE_VX_VY = "9xy0"
    _ANNN_LD_I_ADDR = "Annn"
    _BNNN_JP_V0_ADDR = "Bnnn"
    _CKKK_RND_VX_BYTE = "Cxkk"
    _DXYN_DRW_VX_VY = "Dxyn"
    _E09E_SKP_VX = "Ex9E"
    _EXA1_SKPN_VX = "ExA1"
    _FX07_LD_VX_DT = "Fx07"
    _FX0A_LD_VX_K = "Fx0A"
    _FX15_LD_DT_VX = "Fx15"
    _FX18_LD_ST_VX = "Fx18"
    _FX1E_ADD_I_VX = "Fx1E"
    _FX29_LD_F_VX = "Fx29"
    _FX33_LD_B_VX = "Fx33"
    _FX55_LD_I_VX = "Fx55"
    _FX65_LD_VX_I = "Fx65"


class Decoder:

    @staticmethod
    def decode(op_code):
        res = OpCodes._NO_OPCODE

        # First we will check first 4 bits
        var = op_code & 0xF000
        if var == 0x0000:
            if op_code & 0x00FF == 0x00E0:
                res = OpCodes._00E0_CLS
            elif op_code & 0x00FF == 0x00EE:
                res = OpCodes._00E0_RET
            else:
                res = OpCodes._0NNN_SYS_ADDR
        elif var == 0x1000:
            res = OpCodes._1NNN_JP_ADDR
        elif var == 0x2000:
            res = OpCodes._2NNN_CALL_ADDR
        elif var == 0x3000:
            res = OpCodes._3XKK_SE_VX_BYTE
        elif var == 0x4000:
            res = OpCodes._4XKK_SNE_VX_BYTE
        elif var == 0x5000:
            res = OpCodes._5XY0_SE_VX_VY
        elif var == 0x6000:
            res = OpCodes._6XKK_LD_VX_BYTE
        elif var == 0x7000:
            res = OpCodes._7XKK_ADD_VX_BYTE
        elif var == 0x8000:
            last_digit = op_code & 0x000F
            switch_map = {
                0x0: OpCodes._8XY0_LD_VX_VY,
                0x1: OpCodes._8XY1_OR_VX_VY,
                0x2: OpCodes._8XY2_AND_VX_VY,
                0x3: OpCodes._8XY3_XOR_VX_VY,
                0x4: OpCodes._8XY4_ADD_VX_VY,
                0x5: OpCodes._8xy5_SUB_VX_VY,
                0x6: OpCodes._8XY6_SHR_VX,
                0x7: OpCodes._8XY7_SUBN_VX_VY,
                0xE: OpCodes._820E_SHL_VX,
            }
            res = switch_map[last_digit]
        elif var == 0x9000:
            res = OpCodes._9XY0_SNE_VX_VY
        elif var == 0xA000:
            res = OpCodes._ANNN_LD_I_ADDR
        elif var == 0xB000:
            res = OpCodes._BNNN_JP_V0_ADDR
        elif var == 0xC000:
            res = OpCodes._CKKK_RND_VX_BYTE
        elif var == 0xD000:
            res = OpCodes._DXYN_DRW_VX_VY
        elif var == 0xE000:
            if op_code & 0xF0FF == 0xE09E:
                res = OpCodes._E09E_SKP_VX
            elif op_code & 0xF0FF == 0xE0A1:
                res = OpCodes._EXA1_SKPN_VX
        elif var == 0xF000:
            last_digit = op_code & 0x00FF
            switch_map = {
                0x07: OpCodes._FX07_LD_VX_DT,
                0x0A: OpCodes._FX0A_LD_VX_K,
                0x15: OpCodes._FX15_LD_DT_VX,
                0x18: OpCodes._FX18_LD_ST_VX,
                0x1E: OpCodes._FX1E_ADD_I_VX,
                0x29: OpCodes._FX29_LD_F_VX,
                0x33: OpCodes._FX33_LD_B_VX,
                0x55: OpCodes._FX55_LD_I_VX,
                0x65: OpCodes._FX65_LD_VX_I,
            }
            res = switch_map[last_digit]

        return res
