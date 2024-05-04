from tui import get_user_args
import alist
import pathlib


def _get_id_from_file_name(name):
    n = pathlib.Path(name).stem
    n = n.replace('.', '_')
    n = n.replace('-', '_')
    return n.upper()


def _list_to_file(file_name, str_list):
    with open(file_name, 'w') as f:
        f.write("\n".join(str_list))


def write_files(all_instructions, code_file, header_file, lst_file):
    c_content = []
    header_content = ["#pragma once", "", "// AUTO GENERATED HEADER!"]
    lst_content = ["# WIMAX LDPC ALIST Encoding"]

    start_address = 0
    for w in all_instructions:
        a_file = w['alist_file']
        alist_id = w['id']
        instructions = w['inst']
        header_content.append(f'#define _WLAE_INDEX_{alist_id} 0x{start_address:04X} // {start_address}')
        lst_content.append(f"# {alist_id} file:{a_file}")
        for index, inst in enumerate(instructions):
            addr = start_address + index
            code = alist.instruction_to_code(inst)
            asm = alist.instruction_to_string(inst)
            lst_content.append(f'{addr:04X}: {code:08X} # {asm}')
            c_content.append(f'{code:08X}')
        lst_content.append(f'#####################################')
        lst_content.append("")
        start_address = start_address + len(instructions)

    header_content.append("")
    header_content.append(f'#define _WLAE_LAST_INSTR_ 0x{start_address:04X} // {start_address}')

    _list_to_file(code_file, c_content)
    _list_to_file(header_file, header_content)
    _list_to_file(lst_file, lst_content)


def main():
    args = get_user_args()
    all_instructions = []
    for f in args.alist:
        proto_matrix = alist.parse_alist(f, num_block_columns=24)
        instructions = alist.assemble_instructions(proto_matrix, min_pipe_stages=args.pipe)
        all_instructions.append(dict(
            alist_file=f,
            id=_get_id_from_file_name(f),
            inst=instructions
        ))

    out_file = pathlib.Path(args.out)
    header_file = out_file.with_suffix('.h')
    lst_file = out_file.with_suffix('.lst')
    write_files(all_instructions, out_file, header_file, lst_file)
