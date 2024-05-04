class Coder:
    def __init__(self):
        self.code = 0

    def add(self, bit_pos, value):
        new_opcode = value << bit_pos
        self.code = self.code | new_opcode

    def __repr__(self):
        return f"{self.code:08x}"
