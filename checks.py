#!/usr/bin/env python3

"""Check the given ted file (which should have been written by join-ted.py)."""

# pylama:ignore=E501

import sys
import csv

from common import log


def _check_ted_links(rec):
    tid = rec["ted_id"].strip()
    if not tid:
        return True

    exp_ted = "http://www.ted.com/talks/view/id/{}".format(tid)
    exp_transcript = "http://www.ted.com/talks/view/id/{}/transcript?language=en".format(tid)

    act_ted = rec["TED_URL"]
    act_transcript = rec["transcript_URL"]

    ok = True
    if act_ted != exp_ted or act_transcript != exp_transcript:
        ok = False
        log("%s: url mismatch...", tid)
        if act_ted != exp_ted:
            log("  ted, expected %s go %s", exp_ted, act_ted)
        if act_transcript != exp_transcript:
            log("  ted, expected %s go %s", exp_transcript, act_transcript)

    return ok


def main():
    """Entry point."""
    CHECKS = [
        _check_ted_links,
    ]
    ok = True
    for r in csv.DictReader(sys.stdin):
        for c in CHECKS:
            ok = ok or c(r)

    if not ok:
        log("There was a failed check: will fail")
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
