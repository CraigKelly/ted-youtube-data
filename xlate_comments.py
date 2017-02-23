#!/usr/bin/env python3

"""Read all comment JSON files in specified dir and write CSV to stdout."""

# pylama:ignore=E501,D213

# TODO: include in big ZIP file

import sys
import argparse
import os
import glob
import csv
import json
import datetime

from common import log

OUTPUT_COLS = [
    'comment_id',
    'parent_id',
    'discussion_id',
    'user_id',
    'name',
    'profile_id',
    'profile_pic',
    'profile_score',
    'date',
    'date_activity',
    'deleted',
    'deleted_reason',
    'expired',
    'level',
    'replies',
    'score',
    'comment',
]


def ws(s):
    """Normalize whitespace."""
    return ' '.join(s.strip().split())


def dt(s):
    """Convert timestamps found in comment record."""
    # Note that unlike the JS-based timestamp we've seen from TED, this one is
    # compatible with Python timestamps. We assume UTC since that's what we've
    # seen in the past
    if not s:
        return ''
    dt = datetime.datetime.utcfromtimestamp(int(s))
    return dt.strftime("%Y-%m-%d")


def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", help="input directory")
    parser.add_argument("-o", "--out", help="output CSV file")
    args = parser.parse_args()

    if not args.dir or not os.path.isdir(args.dir):
        raise ValueError("No directory specified")
    if not args.out:
        raise ValueError("No output CSV file specified")

    with open(args.out, "w") as outfh:
        outp = csv.writer(outfh, quoting=csv.QUOTE_NONNUMERIC)
        outp.writerow(OUTPUT_COLS)

        files, records, written = 0, 0, 0
        for fn in glob.glob(os.path.join(args.dir, "*.json")):
            log("Reading %s", fn)
            files += 1
            with open(fn) as inp:
                for line in inp:
                    rec = json.loads(line)
                    records += 1

                    rec['date'] = dt(rec.get('date', ''))
                    rec['date_activity'] = dt(rec.get('date_activity', ''))
                    rec['comment'] = ws(rec.get('comment', ''))

                    outp.writerow([rec.get(c, '') for c in OUTPUT_COLS])
                    written += 1

    log("Read:  %12d files", files)
    log("  with %12d records", records)
    log("Wrote: %12d lines of output", written)


if __name__ == '__main__':
    main()
