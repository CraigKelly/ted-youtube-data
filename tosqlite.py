#!/usr/bin/env python3

"""Write stdin to specified sqlite file."""

# pylama:ignore=E501

import argparse
import sys
import os
import csv
import sqlite3

from common import log


def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--out", help="output sqlite file")
    args = parser.parse_args()

    if os.path.isfile(args.out):
        os.remove(args.out)

    conn = sqlite3.connect(args.out)
    cur = conn.cursor()

    headers = None
    count = 0
    inp = csv.reader(sys.stdin)

    for rec in inp:
        if not headers:
            headers = ','.join(rec)
            sql = "create table ted ({})".format(headers)
            cur.execute(sql)
            conn.commit()
            log("CREATED: %s", sql)
            insert_sql = "insert into ted ({}) values ({})".format(
                headers,
                ','.join(['?'] * len(rec))
            )
            continue

        cur.execute(insert_sql, rec)
        count += 1
        if count % 1000 == 0:
            conn.commit()
            log("Inserted %d records", count)

    conn.commit()
    log("DONE: %d records", count)


if __name__ == '__main__':
    main()
