#!/usr/bin/env python3
"""Map characterization artifacts to extracted candidates by file/contract rules."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDS = [
    "candidate_id",
    "project",
    "file",
    "candidate_type",
    "oracle_id",
    "oracle_status",
    "coverage_reason",
]


def characterization_passed(path: Path) -> bool:
    if not path.exists():
        return False
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return bool(rows and rows[0].get("status") == "PASS")


def map_candidate(
    row: dict[str, str],
    oracle_passed: bool,
    oracle_id_arg: str,
    stable_files: set[str],
    review_types: set[str],
) -> tuple[str, str, str]:
    if not oracle_passed:
        return "", "pending", "No passing characterization artifact."

    if row["file"] in stable_files:
        return (
            oracle_id_arg,
            "stable",
            "Characterization route exercises this entrypoint/template/rendering path.",
        )

    if row["candidate_type"] in review_types and row.get("dom_selectors"):
        return (
            f"{oracle_id_arg}_partial",
            "needs_review",
            "Candidate has rendered-output contract; manual route mapping required.",
        )

    return "", "pending", "No route-level oracle mapped yet."


def main() -> int:
    parser = argparse.ArgumentParser(description="Map characterization coverage to candidates.")
    parser.add_argument("--candidate-csv", required=True, type=Path)
    parser.add_argument("--characterization-csv", required=True, type=Path)
    parser.add_argument("--oracle-id", required=True)
    parser.add_argument("--stable-file", action="append", default=[])
    parser.add_argument(
        "--review-type",
        action="append",
        default=["mixed_php_html", "form_handling", "mixed_php_html_sql"],
    )
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    oracle_passed = characterization_passed(args.characterization_csv)
    rows = []
    with args.candidate_csv.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            oracle_id, status, reason = map_candidate(
                row,
                oracle_passed,
                args.oracle_id,
                set(args.stable_file),
                set(args.review_type),
            )
            rows.append(
                {
                    "candidate_id": row["candidate_id"],
                    "project": row["project"],
                    "file": row["file"],
                    "candidate_type": row["candidate_type"],
                    "oracle_id": oracle_id,
                    "oracle_status": status,
                    "coverage_reason": reason,
                }
            )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["oracle_status"]] = counts.get(row["oracle_status"], 0) + 1
    print(f"Wrote {args.out}")
    for key, value in sorted(counts.items()):
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
