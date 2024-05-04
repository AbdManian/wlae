import argparse


def get_user_args(given_args=None):
    parser = argparse.ArgumentParser(
        prog="wlae",
        description="WIMAX LDPC Alist Encoder"
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output file name default="out"',
        default='out',
        metavar='FILENAME'
    )

    parser.add_argument(
        '--pipe',
        type=int,
        help='Number of stages for shift/store pipe default=8',
        default=8,
        metavar='PIPE-STAGES'
    )

    parser.add_argument(
        'alist',
        nargs='+',
        help='Alist files to be encoded',
        metavar='ALIST-FILE'
    )

    args = parser.parse_args(args=given_args)
    return args

