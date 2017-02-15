#!/usr/bin/env python3

"""Get transcript links from stdin and write to specified dir."""

# pylama:ignore=E501,D213

import argparse
import os
import glob

from bs4 import BeautifulSoup

from common import log


def ws(s):
    """Normalize whitespace."""
    return ' '.join(s.strip().split())


def fmtts(ts):
    """Given a timestamp in seconds, return a formatted string."""
    hr, mn, sec = 0.0, 0.0, ts
    while sec > 60.0:
        sec -= 60.0
        mn += 1.0
    while mn > 60.0:
        mn -= 60.0
        hr += 1.0
    return "{:02.0f}:{:02.0f}:{:07.4f}".format(hr, mn, sec)


def lines(html):
    """Yield (second,text) as found in the HTML."""
    soup = BeautifulSoup(html, 'html5lib')
    for d in soup.find_all('span'):
        cls = d.get('class')
        if not cls or cls[0] != 'talk-transcript__fragment':
            continue
        ts = float(d.get('data-time')) / 1000.0
        txt = ws(d.get_text())
        yield (ts, txt)


def xlate_one(filename):
    """Retrieval logic for a single URL."""
    if not os.path.isfile(filename):
        raise ValueError("Could not find input file " + filename)

    return list(lines(open(filename).read()))


def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", help="output directory")
    args = parser.parse_args()

    if not args.dir or not os.path.isdir(args.dir):
        raise ValueError("No directory specified")

    def outfile(fn):
        return os.path.join(args.dir, fn)

    for inp in glob.glob(outfile("*.html")):
        lines = xlate_one(inp)
        scriptfn = inp.replace(".html", ".transcript")
        textfn = inp.replace(".html", ".txt")
        with open(scriptfn, "w") as outp:
            for ts, txt in lines:
                ts = fmtts(ts)
                outp.write("{} {}\n".format(ts, txt))
        with open(textfn, "w") as outp:
            outp.write(ws(' '.join(txt for _, txt in lines)))
        log("Wrote transcript %s and text %s", scriptfn, textfn)


if __name__ == '__main__':
    main()
