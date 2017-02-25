#!/usr/bin/env python3

"""Read all comment JSON files in specified dir and write CSV to stdout."""

# pylama:ignore=E501,D213

import argparse
import os
import glob
import csv
import json
import datetime

from common import log

OUTPUT_COLS = [
    'ted_id',          # from file name - the TED ID in ted_joined.csv
    'comment_id',      # identifier for the comment
    'parent_id',       # identifier of the parent comment in the thread (or 0 if no parent)
    'discussion_id',   # unique discussion/thread identifier (probably?)
    'user_id',         # user identifier - these are unique and correlated with profile_id
    'name',            # user name
    'profile_id',      # user profile id - used if you want the user's profile page at http://www.ted.com/profiles/{profile_id}
    'profile_pic',     # user profile pic
    'profile_score',   # user profile score, AKA "TedCred" (see http://www.ted.com/participate/discuss/tedcred)
    'date',            # Date of comment posting (?)
    'date_activity',   # Date of last activity on comment (?) - note there are 9 records where date_activity < date
    'deleted',         # true if comment was delete
    'deleted_reason',  # reason deleted=True
    'level',           # Assumed to be level of comment in thread (distribution of values seems to bear this out)
    'replies',         # Number of replies
    'score',           # Comment score - unknown scoring mechanism (59% are 0)
    'comment',         # Actual comment with whitespace normalized
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
            basefn = os.path.split(fn)[-1]
            ted_id = int(os.path.splitext(basefn)[0])

            log("Reading %s (TED_ID=%d)", fn, ted_id)
            files += 1
            with open(fn) as inp:
                for line in inp:
                    rec = json.loads(line)
                    records += 1

                    rec['ted_id'] = ted_id
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
