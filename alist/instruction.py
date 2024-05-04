from dataclasses import dataclass
from .coder import Coder


@dataclass
class Instruction:
    row_info: int = 0
    column: int = 0
    shift: int = 0
    pkt_addr_incr: bool = False
    rotate_sel: int = 0
    sum_init: bool = False
    sum_store: bool = False
    parity_store: bool = False
    p1_store: bool = False
    result_store: bool = False
    result_new_pkt: bool = False
    final_instr: bool = False


def instruction_to_code(instr: Instruction):
    c = Coder()
    c.add(0, instr.column)
    c.add(7, instr.final_instr)
    c.add(8, instr.shift)
    c.add(15, instr.pkt_addr_incr)
    c.add(16, instr.rotate_sel)
    c.add(18, instr.sum_init)
    c.add(19, instr.sum_store)
    c.add(20, instr.parity_store)
    c.add(21, instr.p1_store)
    c.add(22, instr.result_store)
    c.add(23,instr.result_new_pkt)
    return c.code


def instruction_to_string(instr: Instruction):
    sections = []
    if instr.rotate_sel == 0:
        data_section = f"data{instr.column}"
    elif instr.rotate_sel == 1:
        data_section = f"lp"
    else:
        data_section = f"p0"
    sections.append(data_section)

    sections.append(f"shift{instr.shift}")

    if instr.sum_init:
        sections.append("init")

    if instr.sum_store:
        sections.append("+")

    if not instr.sum_store and not instr.sum_init:
        sections = []

    if instr.parity_store:
        sections.append("parity-store")

    if instr.p1_store:
        sections.append("p0-store")

    if instr.result_new_pkt:
        sections.append("new-pkt")

    if instr.result_store:
        sections.append("result-store")

    if instr.final_instr:
        sections.append("FINAL")

    if not sections:
        sections.append("nop")

    row_info = f"row={instr.row_info}."
    return row_info + ".".join(sections)

