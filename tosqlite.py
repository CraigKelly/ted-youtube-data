#!/usr/bin/env python3

"""Write stdin to specified sqlite file."""

# pylama:ignore=E501,D213

import argparse
import os
import csv
import sqlite3

from common import log


def edit_distance(s1, s2):
    """Edit distance for two strings.

    This is the Levenshtein distance, adapted from the code at
    https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python

    The return value is the "traditional" distance metric divided by the len of
    the longer string, so the return value is in the range [0.0, 1.0]
    """
    s1 = str(s1).strip().lower()
    s2 = str(s2).strip().lower()
    z = max(len(s1), len(s2))
    if z == 0:
        return 0.0
    if len(s1) < len(s2):
        s1, s2 = s2, s1
    if len(s2) == 0:  # len(s1) >= len(s2)
        return len(s1) / z

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1  # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1        # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1] / z


def reader_to_table(conn, tabname, csvreader):
    """CSV to table routine."""
    headers = None
    count = 0
    cur = conn.cursor()

    for rec in csvreader:
        if not headers:
            headers = ','.join(rec)
            sql = "create table {} ({})".format(tabname, headers)
            cur.execute(sql)
            conn.commit()
            log("CREATED: %s", sql)
            insert_sql = "insert into {} ({}) values ({})".format(
                tabname,
                headers,
                ','.join(['?'] * len(rec))
            )
            continue

        cur.execute(insert_sql, rec)
        count += 1
        if count % 50000 == 0:
            conn.commit()
            log("    Inserted %d records", count)

    conn.commit()
    log("BASE TABLE DONE: %d records", count)


def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--joined", required=True, help="input ted joined csv file")
    parser.add_argument("-c", "--comments", required=True, help="input comments csv file")
    parser.add_argument("-o", "--out", required=True, help="output sqlite file")
    args = parser.parse_args()

    if os.path.isfile(args.out):
        os.remove(args.out)

    conn = sqlite3.connect(args.out)
    conn.create_function("edist", 2, edit_distance)

    reader_to_table(conn, "ted", csv.reader(open(args.joined)))
    reader_to_table(conn, "comments", csv.reader(open(args.comments)))

    # Now create author_match table
    log("Running matching_speakers.sql")
    cur = conn.cursor()

    with open("matching_speakers.sql") as f:
        sql = f.read().strip()

    with conn:
        for cmd in sql.split(';'):
            if not cmd:
                continue
            cur.execute(cmd)
    cur.execute("select count(*) from matching_speakers")
    log("matching_speakers record count: %d", cur.fetchone()[0])

    conn.close()


if __name__ == '__main__':
    main()
