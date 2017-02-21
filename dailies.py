#!/usr/bin/env python3

"""Read json data from stdin and write daily views CSV to stdout."""

# pylama:ignore=E501,C901

import csv
import sys
import json
import datetime

from common import log


# TODO: join in the daily views with day from ytscrape/ytcrawl.parsed.json

OUTPUT_COLS = [
    "youtube_id",
    "day",
    "view_count"
]


def ts_to_day(ts):
    """Convert the JS-style timestamp to a year-month-day string."""
    dt = datetime.datetime.utcfromtimestamp(int(ts) / 1000)
    return dt.strftime("%Y-%m-%d")


def main():
    """Entry point."""
    outp = csv.writer(sys.stdout, quoting=csv.QUOTE_NONNUMERIC)
    outp.writerow(OUTPUT_COLS)

    recs, written = 0, 0
    for line in sys.stdin:
        rec = json.loads(line)
        recs += 1

        ytid = rec["YTID"]
        days = rec["day"]["data"]
        views = rec["views"]["daily"]["data"]

        for d, v in zip(days, views):
            outp.writerow([ytid, d, v])
            written += 1

    log("Records read: %12d", recs)
    log("       wrote: %12d", written)


if __name__ == '__main__':
    main()
