import numpy as np
from .instruction import Instruction


def file_to_lines(file_name: str):
    with open(file_name, 'r') as f:
        ret = f.readlines()

    return list(filter(None, map(lambda s: s.strip(), ret)))


def line_to_int(line: str):
    return [int(x) for x in line.split()]


def line_to_row(line: str, sub_matrix_size: int, num_block_columns: int):
    values = line_to_int(line)
    ret = np.full(num_block_columns, -1)
    for x in values:
        if not x:
            continue
        index = x - 1
        col = index // sub_matrix_size
        shift = index % sub_matrix_size
        ret[col] = shift
    return ret


def parse_alist(file_name: str, num_block_columns=24):
    alist_lines = file_to_lines(file_name)
    pkt_size, parity_size = line_to_int(alist_lines[0])
    sub_matrix_size = pkt_size // num_block_columns
    num_rows = parity_size // sub_matrix_size

    proto_matrix = np.full((num_rows, num_block_columns), -1)

    start_index = 4 + pkt_size  # 4: first lines, pkt_size: columns
    for i in range(num_rows):
        index = start_index + i*sub_matrix_size
        proto_matrix[i] = line_to_row(alist_lines[index], sub_matrix_size, num_block_columns)

    return proto_matrix


def assemble_instructions(proto_matrix: np.array, min_pipe_stages: int = 8):
    num_parity, num_block = proto_matrix.shape
    num_data = num_block - num_parity

    data = proto_matrix[:, :num_data]
    parity = proto_matrix[:, num_data:]
    result = []
    first_parity_instr = []
    for r in range(num_parity):
        for c in range(num_data):
            shift_cnt = data[r, c]
            if shift_cnt < 0:
                continue
            i = Instruction()
            i.row_info = r
            i.column = c
            i.shift = shift_cnt
            i.sum_store = True

            first_parity_instr.append(i)

    first_parity_instr[0].sum_init = True
    first_parity_instr[-1].parity_store = True
    first_parity_instr[-1].p1_store = True
    first_parity_instr[-1].result_store = True
    first_parity_instr[-1].result_new_pkt = True

    result.extend(first_parity_instr)

    for r in range(num_parity - 1):
        current_row_instr = []
        for c in range(num_data):
            shift_cnt = data[r, c]
            if shift_cnt < 0:
                continue
            i = Instruction()
            i.row_info = r
            i.column = c
            i.shift = shift_cnt
            i.sum_store = True
            current_row_instr.append(i)

        current_row_instr[0].sum_init = True

        p1_shift = parity[r, 0]

        if r == 0:
            i1 = Instruction()
            i1.row_info = r
            i1.shift = p1_shift
            i1.rotate_sel = 2
            i1.sum_store = True
            i1.parity_store = True
            i1.result_store = True
            current_row_instr.append(i1)
        else:
            req_stages = min_pipe_stages - len(current_row_instr)
            for _ in range(req_stages):
                nop = Instruction()
                nop.row_info = r
                current_row_instr.append(nop)

            if p1_shift == 0:
                i2 = Instruction()
                i2.row_info = r
                i2.rotate_sel = 2
                i2.sum_store = True
                current_row_instr.append(i2)
            i1 = Instruction()
            i1.row_info = r
            i1.rotate_sel = 1
            i1.sum_store = True
            i1.parity_store = True
            i1.result_store = True
            current_row_instr.append(i1)
        if r == num_parity - 2:
            current_row_instr[-1].final_instr = True
            current_row_instr[-1].pkt_addr_incr = True
            # Insert extra nop after final instruction
            nop = Instruction()
            nop.row_info = r
            current_row_instr.append(nop)

        result.extend(current_row_instr)
    return result
