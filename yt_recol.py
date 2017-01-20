#!/usr/bin/env python3

"""Fix columns on YT csv file (via stdin to stdout)."""

import sys
import csv


def log(msg, *args):
    """Log to stderr with optional formatting."""
    if args:
        msg = msg % args
    sys.stderr.write(msg)
    sys.stderr.write("\n")
    sys.stderr.flush()


def main():
    """Entry point."""
    inp = csv.reader(sys.stdin)
    outp = csv.writer(sys.stdout, quoting=csv.QUOTE_NONNUMERIC)

    headers = None
    read, written = 0, 0

    for rec in inp:
        if not headers:
            headers = dict([(h, i) for i, h in enumerate(rec)])
            # TODO: check headers we need
            outp.writerow(rec)
            continue
        read += 1

        # TODO: Split Descrip|Speaker into 2 columns: Descrip and Speaker (+2)
        # TODO: don't output Descrip|Speaker in final file (-1)
        # TODO: Extract YT id from YTLink col (+1)
        # TODO: insure net col change is 2 (2-1+1 from above)

        outp.writerow(rec)
        written += 1

    log("Read %d, Wrote %d", read, written)


if __name__ == '__main__':
    main()
