#!/usr/bin/env python3

"""Get comments from the TED Talk page.

Note that the we can access the comments page-by-page via a web API, *but* we
need the threadId (which is NOT the same as the TED ID).
"""

# pylama:ignore=E501,D213


import argparse
import sys
import os
import csv
import requests
import json
import re

from common import log

tid_re = re.compile(r'\"threadId\":\s*([0-9]+),')


def comment_walker(comment_list):
    """Recursively walk and yield comments."""
    # May be list or dict (thanks, TED)
    if type(comment_list) is dict:
        comment_list = list(comment_list.values())  # convert to list

    for comment in comment_list:
        copy = dict(comment, children=None)
        del copy["children"]
        if copy:
            yield copy

        children = comment.get("children", [])
        if children:
            for child in comment_walker(children):
                if child:
                    yield child


def retrieve_one(ted_url, out_filename):
    """Retrieval logic for a single URL."""
    if os.path.isfile(out_filename):
        log("SKIP: %s", ted_url)
        return

    # Get the talk page
    resp = requests.get(ted_url)
    if resp.status_code == 404:
        log("MISS[404]: %s", ted_url)
        return
    resp.raise_for_status()  # all other codes get an exception

    # extract the threadId
    matches = tid_re.findall(resp.text)
    if len(matches) != 1:
        log("ERROR[no threadid]: %s", ted_url)
        return
    tid = matches[0].strip()
    if not tid:
        log("ERROR[blank threadid]: %s", ted_url)
        return

    # get all comments
    comments = {}  # comment_id => comment
    page = 0
    while True:
        page += 1  # next page
        url = "http://www.ted.com/conversation_forums/%s?page=%d&per_page=75&sort=newest" % (tid, page)
        resp = requests.get(url, headers={
            "Host": "www.ted.com",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "X-Requested-With": "XMLHttpRequest",
        })

        presize = len(comments)

        # The thread is a list, but each item is a dict with "fake" keys
        all_comments = []
        for one in resp.json().get("discussion_thread", {}).get("thread", []):
            all_comments.extend(list(one.values()))

        for comment in comment_walker(all_comments):
            comments[int(comment["comment_id"])] = comment

        if len(comments) == presize:
            break  # nothing new found

    # write comments to the file
    with open(out_filename, "w") as fh:
        for cid, comment in sorted(comments.items()):
            fh.write(json.dumps(comment) + '\n')

    log("WRITE: [comments=%d] %s", len(comments), ted_url)


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
        ted_url = rec.get("TED_URL", None)

        if not ted_url:
            log("Skipping comments for [%s]-[%s]", ted_id, youtube_id)
            continue

        if not ted_id:
            raise ValueError("Invalid record: TED_URL with missing ted_id " + repr(rec))

        fn = outfile("{}.json".format(ted_id))
        retrieve_one(ted_url, fn)

        count += 1

    with open(completed, "w") as fh:
        fh.write("Completed output, transcript count was: %d\n" % count)


if __name__ == '__main__':
    main()
