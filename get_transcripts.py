#!/usr/bin/env python3

"""Get transcript links from stdin and write to specified dir."""

# pylama:ignore=E501,D213

import argparse
import sys
import os
import csv
import requests

from common import log


def retrieve_one(transcript_url, out_filename):
    """Retrieval logic for a single URL."""
    if os.path.isfile(out_filename):
        log("SKIP: %s", transcript_url)
        return

    resp = requests.get(transcript_url)
    if resp.status_code == 404:
        log("MISS[404]: %s", transcript_url)
        return
    resp.raise_for_status()  # all other codes get an exception

    with open(out_filename, "w") as fh:
        fh.write(resp.text)
    log("WRITE: %s", transcript_url)


def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", help="output directory")
    args = parser.parse_args()

    if not args.dir or not os.path.isdir(args.dir):
        raise ValueError("No directory specified")

    def outfile(fn):
        return os.path.join(args.dir, fn)

    completed = outfile("get-completed")
    if os.path.isfile(completed):
        log("Removing previous file: %s", completed)
        os.remove(completed)

    count = 0
    inp = csv.DictReader(sys.stdin)

    for rec in inp:
        ted_id = rec.get("ted_id", "")
        youtube_id = rec.get("youtube_id", "")
        transcript_url = rec.get("transcript_URL", None)

        if not transcript_url:
            log("Skipping transcript for [%s]-[%s]", ted_id, youtube_id)
            continue

        if not ted_id:
            raise ValueError("Invalid record: transcript_URL with missing ted_id " + repr(rec))

        fn = outfile("{}.html".format(ted_id))
        retrieve_one(transcript_url, fn)

        count += 1

    with open(completed, "w") as fh:
        fh.write("Completed output, transcript count was: %d\n" % count)


if __name__ == '__main__':
    main()
