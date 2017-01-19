#!/usr/bin/env python3

"""Clean up any "bad" characters."""

import sys

from unidecode import unidecode


def main():
    """Entry point."""
    buf = sys.stdin.read()
    sys.stdout.write(unidecode(str(buf)))


if __name__ == '__main__':
    main()
