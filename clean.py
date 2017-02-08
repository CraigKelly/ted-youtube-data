#!/usr/bin/env python3

"""Clean up any "bad" characters."""

import os
import argparse
import csv

from unidecode import unidecode

from common import log


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
        read = csv.reader(inp)
        with open(args.output, "w", encoding="utf-8") as outp:
            write = csv.writer(outp)
            for rec in read:
                write.writerow([unidecode(i) for i in rec])


if __name__ == '__main__':
    main()
