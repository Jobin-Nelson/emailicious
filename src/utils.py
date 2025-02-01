import sys
from enum import IntEnum
from typing import NoReturn


class ExitCode(IntEnum):
    CONFIG_NOT_FOUND = 1
    EMAIL_NOT_SEND = 2
    AUTH_CODE_NOT_ENTERED = 3
    ACCESS_TOKEN_NOT_FOUND = 4


def bail(message: str, code: ExitCode) -> NoReturn:
    '''Prints a message and exits with a code'''
    print(message, file=sys.stderr)
    sys.exit(code.value)
