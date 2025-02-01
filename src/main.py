#!/usr/bin/env python3
'''This module sends email updates'''

import argparse

from gmail import gmail_main


def main() -> int:
    '''Sends an email update for today'''

    parser = argparse.ArgumentParser(description='Send email updates')
    parser_group = parser.add_mutually_exclusive_group(required=True)
    parser_group.add_argument(
        '-g', '--gmail', action='store_true', help='Send email using Gmail'
    )
    parser_group.add_argument(
        '-o', '--outlook', action='store_true', help='Send email using Outlook'
    )

    args = parser.parse_args()
    if args.gmail:
        return gmail_main()

    # TODO: Implement Outlook
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
