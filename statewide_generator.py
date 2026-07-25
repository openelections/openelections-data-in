#!/usr/bin/env python3
"""Regenerate a statewide precinct-level CSV by concatenating each county's
precinct-level source files (under <year>/counties/) for a given election.
"""
import argparse
import csv
import glob
import os

BREAKDOWN_COLUMNS = ["absentee", "early_voting", "election_day", "mail", "provisional"]
BASE_COLUMNS = ["county", "precinct", "office", "district", "candidate", "party", "votes"]


def _county_files(year, election):
    pattern = os.path.join(year, "counties", f"{election}*precinct.csv")
    return sorted(glob.glob(pattern))


def generate_headers(year, election):
    """Print, for each county file, any headers beyond the standard columns."""
    for fname in _county_files(year, election):
        with open(fname, newline="", encoding="utf-8-sig") as csvfile:
            headers = next(csv.reader(csvfile))
        print(fname, sorted(set(headers) - set(BASE_COLUMNS)))


def generate_offices(year, election):
    """Write every distinct office found across county files to offices.csv."""
    offices = []
    seen = set()
    for fname in _county_files(year, election):
        with open(fname, newline="", encoding="utf-8-sig") as csvfile:
            for row in csv.DictReader(csvfile):
                office = row["office"]
                if office not in seen:
                    seen.add(office)
                    offices.append(office)

    out_path = os.path.join(year, "offices.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as csv_outfile:
        writer = csv.writer(csv_outfile, lineterminator="\n")
        writer.writerows([[office] for office in offices])
    print(f"wrote {len(offices)} offices to {out_path}")


def generate_consolidated_file(year, election, output_file):
    """Concatenate every county precinct file into one statewide precinct file.

    Every row is included regardless of office - an office allowlist here
    would silently drop down-ballot races from the statewide file. Breakdown
    columns (absentee/early_voting/election_day/mail/provisional) are
    included if ANY input file has them; a row from a file that lacks a
    given column is left blank for it rather than the column being dropped
    from the whole output.
    """
    files = _county_files(year, election)
    if not files:
        raise SystemExit(f"no county precinct files found for {year}/{election}")

    breakdown_cols = []
    for fname in files:
        with open(fname, newline="", encoding="utf-8-sig") as csvfile:
            headers = next(csv.reader(csvfile))
        for col in BREAKDOWN_COLUMNS:
            if col in headers and col not in breakdown_cols:
                breakdown_cols.append(col)

    output_columns = BASE_COLUMNS + breakdown_cols

    results = []
    for fname in files:
        with open(fname, newline="", encoding="utf-8-sig") as csvfile:
            for row in csv.DictReader(csvfile):
                results.append([row.get(col, "") for col in output_columns])

    with open(output_file, "w", newline="", encoding="utf-8") as csv_outfile:
        writer = csv.writer(csv_outfile, lineterminator="\n")
        writer.writerow(output_columns)
        writer.writerows(results)
    print(f"wrote {len(results)} rows to {output_file}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("year", help="election year directory, e.g. 2018")
    parser.add_argument("election", help="election id prefix, e.g. 20181106")
    parser.add_argument(
        "--command",
        choices=["consolidate", "headers", "offices"],
        default="consolidate",
        help="what to generate (default: consolidate)",
    )
    parser.add_argument(
        "--output",
        help="output path for the consolidated file "
        "(default: <year>/<election>__in__general__precinct.csv)",
    )
    args = parser.parse_args()

    if args.command == "headers":
        generate_headers(args.year, args.election)
    elif args.command == "offices":
        generate_offices(args.year, args.election)
    else:
        output_file = args.output or os.path.join(
            args.year, f"{args.election}__in__general__precinct.csv"
        )
        generate_consolidated_file(args.year, args.election, output_file)


if __name__ == "__main__":
    main()
