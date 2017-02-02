#!/usr/bin/env python3

"""Fix columns on YT csv file (via stdin to stdout)."""

# pylama:ignore=E501

import sys
import csv

OUTPUT_COLS = [
    "Speaker",
    "Descrip",
    "YTLink",
    "ViewStr",
    "TimeStr",
    "Descrip|Speaker",
]

# TODO: read descrips from ted_talks.csv so that we can fill in authors (and ditch this fix dict)
DS_FIXES = {
    "Ideas worth dating": "Ideas worth dating|Rainn Wilson",
    "The Year in Ideas: TED Talks of 2015": "The Year in Ideas: TED Talks of 2015|Various",
    "Clayton Cameron: A-rhythm-etic. The math behind the beats": "A-rhythm-etic. The math behind the beats|Clayton Cameron",
}

DS_BAD_SUFFIX = set([
    "ted talks",
    "ted talk",
    "ted.com"
])


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

    ds_idx = None

    for rec in inp:
        if not headers:
            headers = dict([(h, i) for i, h in enumerate(rec)])
            ds_idx = headers.get("Descrip|Speaker", None)
            if ds_idx is None:
                raise ValueError("Invalid state: no Descrip|Speaker column")
            outp.writerow(OUTPUT_COLS)
            continue

        read += 1

        outrec = dict((col, rec[idx]) for col, idx in headers.items())

        ds = rec[ds_idx].strip()
        ds = DS_FIXES.get(ds, None) or ds

        if "|" in ds:
            # Descrip | Author format (possibly with other endings)
            ds_fields = ds.split("|")
            while ds_fields[-1].strip().lower() in DS_BAD_SUFFIX:
                ds_fields = ds_fields[:-1]
        elif ":" in ds:
            # This is Author: Descrip format (so notice that we need a swap)
            ds_fields = ds.split(":")
            # Swap order - it's backwards from | descrips
            ds_fields[0], ds_fields[1] = ds_fields[1], ds_fields[0]
        else:
            # TODO: look for author from ted_talks.csv (see above todo)
            raise ValueError("Descrip|Speaker unknown fmt [read:%d,written:%d]: %s" % (read, written, rec[ds_idx]))

        if len(ds_fields) != 2:
            raise ValueError("Descrip|Speaker column broken [read:%d,written:%d]: %s" % (read, written, rec[ds_idx]))

        outrec["Descrip"], outrec["Speaker"] = (i.strip() for i in ds_fields)

        outp.writerow([outrec[c] for c in OUTPUT_COLS])
        written += 1

    log("Read %d, Wrote %d", read, written)


if __name__ == '__main__':
    main()
