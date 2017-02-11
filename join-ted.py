#!/usr/bin/env python3

"""Join two specified CSV files and write to stdout."""

# pylama:ignore=E501

# TODO: use manual_map.csv to perform extra mapping

import argparse
import csv
import re
import sys

from common import log

# Not currently used but good for documentation
# TED_COLS = [
#     "id",
#     "speaker",
#     "headline",
#     "URL",
#     "description",
#     "transcript_URL",
#     "month_filmed",
#     "year_filmed",
#     "event",
#     "duration",
#     "date_published",
#     "tags",
# ]
# YT_COLS = [
#     "Speaker",
#     "Descrip",
#     "YTLink",
#     "ViewStr",
#     "TimeStr",
#     "Descrip|Speaker"
# ]

OUTPUT_COLS = [
    "ted_id",
    "youtube_id",  # from YTLink
    "speaker",  # Speaker in YT
    "headline",  # Descrip in YT
    "TED_URL",
    "transcript_URL",
    "youtube_url",  # YTLink
    "month_filmed",
    "year_filmed",
    "event",
    "time_str",  # TimeStr in YT
    "duration",
    "date_published",
    "youtube_title",  # Descrip|Speaker in YT
    "views_text",  # ViewStr in YT
    "tags",
    "description",
]


def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--ted", help="input ted-talks csv file")
    parser.add_argument("-y", "--yt", help="input youtube-ted csv file")
    args = parser.parse_args()

    log("Reading %s", args.ted)
    with open(args.ted) as tedin:
        ted_xref = dict([
            (r["headline"].strip().lower(), r)
            for r in csv.DictReader(tedin)]
        )
    log("Found %d records in %s", len(ted_xref), args.ted)

    log("Reading %s", args.yt)
    with open(args.yt) as ytin:
        yt_xref = dict([
            (r["Descrip"].strip().lower(), r)
            for r in csv.DictReader(ytin)]
        )
    log("Found %d records in %s", len(yt_xref), args.yt)

    ted_keys = set(ted_xref.keys())
    yt_keys = set(yt_xref.keys())

    log("Matched in both files: %d", len(ted_keys & yt_keys))

    log("In TED talks without matching YT: %d", len(ted_keys - yt_keys))
    # for k in ted_keys - yt_keys:
    #     log(" %s: %s", k, ted_xref[k]["URL"])

    log("In YT without matching TED talks: %d", len(yt_keys - ted_keys))
    # for k in yt_keys - ted_keys:
    #     log(" %s: %s", k, yt_xref[k]["YTLink"])

    ytid_re = re.compile("http://www.youtube.com/watch\?v=([-\w]+)")

    outp = csv.writer(sys.stdout, quoting=csv.QUOTE_NONNUMERIC)
    outp.writerow(OUTPUT_COLS)
    for k in sorted(ted_keys | yt_keys):
        ted = ted_xref.get(k, {})
        yt = yt_xref.get(k, {})

        yt_link = yt.get("YTLink", "").strip()
        if not yt_link:
            yt_id = ""
        else:
            yt_matches = ytid_re.findall(yt_link)
            if len(yt_matches) != 1:
                raise ValueError("Invalid YouTube LINK!!!")
            yt_id = yt_matches[0]

        outp.writerow([
            ted.get("id", ""),
            yt_id,
            ted.get("speaker", yt.get("Speaker")),
            ted.get("headline", yt.get("Descrip")),
            ted.get("URL", ""),
            ted.get("transcript_URL", ""),
            yt_link,
            ted.get("month_filmed", ""),
            ted.get("year_filmed", ""),
            ted.get("event", ""),
            yt.get("TimeStr", ""),
            ted.get("duration", ""),
            ted.get("date_published", ""),
            yt.get("Descrip|Speaker", ""),
            yt.get("ViewStr", ""),
            ted.get("tags", ""),
            ted.get("description", ""),
        ])


if __name__ == '__main__':
    main()
