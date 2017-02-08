#!/usr/bin/env python3

"""Fix columns on YT csv file (via stdin to stdout)."""

# pylama:ignore=E501

import sys
import csv

from common import log


OUTPUT_COLS = [
    "Speaker",
    "Descrip",
    "YTLink",
    "ViewStr",
    "TimeStr",
    "Descrip|Speaker",
]

DS_BAD_SUFFIX = set([
    "ted talks",
    "ted talk",
    "ted.com"
])


def main():
    """Entry point."""
    with open("ted_talks.csv") as tedin:
        ted_xref = dict([
            (r["headline"].strip().lower(), r["speaker"])
            for r in csv.DictReader(tedin)]
        )
    log("Found %d mappings in ted_talks.csv", len(ted_xref))

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
        descrip, speaker = '', ''

        if "|" in ds:
            # Descrip | Author format (possibly with other endings)
            ds_fields = ds.split("|")
            while ds_fields[-1].strip().lower() in DS_BAD_SUFFIX:
                ds_fields = ds_fields[:-1]
            descrip, speaker = ds_fields[:2]
        elif ":" in ds:
            # This is Author: Descrip format (so notice that we need a swap)
            ds_fields = ds.split(":")
            # Swapped order and possible embedded colon
            speaker, descrip = ds_fields[0], ':'.join(ds_fields[1:])
        else:
            # only one value - if it is descrip we might know the speaker
            descrip = ds
            speaker = ted_xref.get(ds.strip().lower(), "")

        if not descrip:
            raise ValueError("Descrip|Speaker missing descrip [line:%d]: %s" % (read+1, ds))

        if not speaker:
            log("No speaker known [line:%d]: %s", read+1, ds)

        outrec["Descrip"] = descrip.strip()
        outrec["Speaker"] = speaker.strip()

        outp.writerow([outrec[c] for c in OUTPUT_COLS])
        written += 1

    log("Read %d, Wrote %d", read, written)


if __name__ == '__main__':
    main()
