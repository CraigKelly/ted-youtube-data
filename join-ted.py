#!/usr/bin/env python3

"""Join two specified CSV files and write to stdout."""

# pylama:ignore=E501

import argparse
import csv
import re
import sys

from common import log

# TODO: join in {'commentCount', 'dislikeCount', 'favoriteCount', 'likeCount', 'viewCount'}
#       from ytscrape/basics.json
# TODO: join in {'Shares', 'Subscriptions driven', 'Views', 'Time watched'}
#       from ytscrape/ytcrawl.parsed.json
# TODO: join in the daily views with day from ytscrape/ytcrawl.parsed.json
#       AND remember the JS day ts can be converted with
#       datetime.datetime.utcfromtimestamp(ts/1000))

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

    ted_keys, ted_xref = {}, {}
    log("Reading %s", args.ted)
    with open(args.ted) as tedin:
        for r in csv.DictReader(tedin):
            ted_keys[r["id"].strip().lower()] = r
            ted_xref[r["headline"].strip().lower()] = r
    log("Found %d keys, %d headlines in %s", len(ted_keys), len(ted_xref), args.ted)

    yt_keys, yt_xref = {}, {}
    ytid_re = re.compile("http://www.youtube.com/watch\?v=([-\w]+)")
    log("Reading %s", args.yt)
    with open(args.yt) as ytin:
        for r in csv.DictReader(ytin):
            yt_link = r.get("YTLink", "").strip()
            ytid = None
            if yt_link:
                yt_matches = ytid_re.findall(yt_link)
                if len(yt_matches) != 1:
                    raise ValueError("Invalid YouTube LINK!!!")
                ytid = yt_matches[0]

            r["YTID"] = ytid
            if ytid:
                yt_keys[ytid] = r

            yt_xref[r["Descrip"].strip().lower()] = r
    log("Found %d keys, %d headlines in %s", len(yt_keys), len(yt_xref), args.yt)

    # All our matches, where each entry is (ted_record, yt_record)
    matches = []

    used_heads = set()
    log("Reading manual_map.csv")
    with open("manual_map.csv") as mapin:
        for r in csv.DictReader(mapin):
            tid = r["ted_id"].strip().lower()
            ytid = r["youtube_id"].strip()
            t = ted_keys.get(tid, None)
            yt = yt_keys.get(ytid, None)
            if t and yt:
                matches.append((t, yt))
                used_heads.add(t["headline"].strip().lower())
                used_heads.add(yt["Descrip"].strip().lower())
    log("Matched %d using manual ID pairs", len(matches))

    log("Performing headline matching")
    all_heads = set(ted_xref.keys()) | set(yt_xref.keys())
    for h in all_heads - used_heads:
        t = ted_xref.get(h, {})
        yt = yt_xref.get(h, {})
        matches.append((t, yt))
    log("New Matched Count after headline matching: %d", len(matches))

    outp = csv.writer(sys.stdout, quoting=csv.QUOTE_NONNUMERIC)
    outp.writerow(OUTPUT_COLS)
    for ted, yt in matches:
        outp.writerow([
            ted.get("id", ""),
            yt.get("YTID", ""),
            ted.get("speaker", yt.get("Speaker")),
            ted.get("headline", yt.get("Descrip")),
            ted.get("URL", ""),
            ted.get("transcript_URL", ""),
            yt.get("YTLink", ""),
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
