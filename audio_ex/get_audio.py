#!/usr/bin/env python3

"""Find all TED MP3 audio that we can using their RSS feed."""

# pylama:ignore=E501,D213

import requests
import csv
import sys
import inspect
import re

TED_JOIN = "../ted_joined.csv"
RSS_URL = "http://feeds.feedburner.com/tedtalks_audio"


def log(msg, *args):
    """Log to stderr with optional formatting."""
    if args:
        msg = msg % args
    pre = inspect.getfile(sys._getframe(1)) + ": "
    sys.stderr.write(pre + msg + "\n")
    sys.stderr.flush()
    sys.stdout.flush()


def main():
    """Entry point."""
    log("Reading %s", TED_JOIN)
    ted_ids = dict()
    with open(TED_JOIN) as fh:
        for rec in csv.DictReader(fh):
            tid = rec.get("ted_id", "")
            root_url = rec.get("TED_URL", "")
            if tid and root_url:
                ted_ids[tid] = root_url
    log("... Found %d records", len(ted_ids))

    # "audioDownload":"https://download.ted.com/talks/RobertGordon_2013.mp3?apikey=489b859150fc58263f17110eeb44ed5fba4a3b22"
    mp3_re = re.compile(r'\"audioDownload\":\s*\"(http[^\"]+)\"')
    for ted_id, root_url in ted_ids.items():
        resp = requests.get(root_url)
        if resp.status_code == 404:
            log("MISS[404]: %s", root_url)
            continue
        resp.raise_for_status()  # all other codes get an exception

        matches = mp3_re.findall(resp.text)
        audio_url = None
        if len(matches) == 1:
            audio_url = matches[0].strip()
        if not audio_url:
            log("NOAUDIO: %s", root_url)
            continue

        log("DOWNLOAD MP3: %s", audio_url)
        fn = ted_id + ".mp3"
        data = requests.get(audio_url).content
        with open(fn, "wb") as fh:
            fh.write(data)
        log("WROTE: %s", fn)


if __name__ == '__main__':
    main()
