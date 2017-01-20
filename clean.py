#!/usr/bin/env python3

"""Clean up any "bad" characters."""

import os
import sys
import argparse

from unidecode import unidecode


def log(msg, *args):
    """Log to stderr with optional formatting."""
    if args:
        msg = msg % args
    sys.stderr.write(msg)
    sys.stderr.write("\n")
    sys.stderr.flush()


def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="input csv file to read")
    parser.add_argument("-o", "--output", help="output csv file to create")
    parser.add_argument("-e", "--encoding", help="encoding of the input file")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        raise ValueError("input csv '%s' does not exist" % args.input)
    if not args.encoding:
        raise ValueError("No input encoding given")
    if not args.output:
        raise ValueError("No output csv given")

    if os.path.isfile(args.output):
        log("Removing previous output file %s", args.output)
        os.remove(args.output)

    with open(args.input, "r", encoding=args.encoding) as inp:
        buf = unidecode(inp.read())
        # Only open output file if conversion above successful
        with open(args.output, "w", encoding="utf-8") as outp:
            outp.write(buf)


if __name__ == '__main__':
    main()
