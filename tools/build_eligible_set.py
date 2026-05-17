#!/usr/bin/env python3
"""Build locked eligible candidate set from stable oracle coverage."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDS = [
    "candidate_id",
    "project",
    "file",
    "candidate_type",
    "start_line",
    "end_line",
    "oracle_ids",
    "eligibility_status",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build eligible candidate set.")
    parser.add_argument("--subjects", nargs="+", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    rows = []
    for subject in args.subjects:
        base = Path("results") / "subjects" / subject
        candidates = {row["candidate_id"]: row for row in read_csv(base / "candidates" / "candidates.csv")}
        coverage = read_csv(base / "oracle" / "coverage.csv")
        for row in coverage:
            if row.get("oracle_status") != "stable":
                continue
            candidate = candidates[row["candidate_id"]]
            rows.append(
                {
                    "candidate_id": row["candidate_id"],
                    "project": subject,
                    "file": row["file"],
                    "candidate_type": row["candidate_type"],
                    "start_line": candidate["start_line"],
                    "end_line": candidate["end_line"],
                    "oracle_ids": row.get("oracle_ids", ""),
                    "eligibility_status": "ELIGIBLE_PRE_TREATMENT",
                }
            )

    rows.sort(key=lambda r: (r["project"], r["candidate_id"]))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {args.out}: {len(rows)} eligible candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
