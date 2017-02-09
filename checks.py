#!/usr/bin/env python3

"""Check the given ted file (which should have been written by join-ted.py)."""

# pylama:ignore=E501,E302,E305

import sys
import csv

from functools import wraps

from common import log

CHECKS = []


def check(f):
    """Decorator to specify function is a check."""
    wraps(f)
    CHECKS.append(f)
    return f


@check
def check_ted_links(rec):
    """Insure ted and transcript URL's look correct."""
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


@check
def check_yt_links(rec):
    """Report any youtube links that don't have TED ID's."""
    tid = rec["ted_id"].strip()
    ytlink = rec["youtube_url"].strip()
    if ytlink:
        check_yt_links.ytcount += 1
        if not tid:
            # log(" YT with no TED ID: %s", ytlink)
            check_yt_links.count += 1
    return True
def check_yt_links_report():
    """Final report for above check."""
    log("Count of All YT:            %6d", check_yt_links.ytcount)
    log("Count of YT with no TED ID: %6d", check_yt_links.count)
check_yt_links.count = 0
check_yt_links.ytcount = 0
check_yt_links.report = check_yt_links_report


def main():
    """Entry point."""
    log("Checks: %s", ', '.join([f.__name__ for f in CHECKS]))

    ok = True
    rcount = 0
    for r in csv.DictReader(sys.stdin):
        rcount += 1
        for c in CHECKS:
            ok = c(r) or ok

    for c in CHECKS:
        final = getattr(c, "report", None)
        if callable(final):
            final()

    log("Count of records seen: %d", rcount)

    if not ok:
        log("There was a failed check: will fail")
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
