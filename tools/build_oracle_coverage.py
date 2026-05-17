#!/usr/bin/env python3
"""Build merged oracle coverage from route-to-file mappings."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


FIELDS = [
    "candidate_id",
    "project",
    "file",
    "candidate_type",
    "oracle_status",
    "oracle_ids",
    "coverage_reason",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def char_passed(path: Path) -> bool:
    if not path.exists():
        return False
    rows = read_csv(path)
    return bool(rows and rows[0].get("status") == "PASS")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build merged candidate oracle coverage.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--candidate-csv", required=True, type=Path)
    parser.add_argument("--routes-json", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    routes = json.loads(args.routes_json.read_text(encoding="utf-8"))
    stable_by_file: dict[str, list[str]] = {}
    review_types = set(routes.get("review_types", ["mixed_php_html", "form_handling", "mixed_php_html_sql"]))

    for route in routes["routes"]:
        char_file = Path(route["characterization_csv"])
        if not char_passed(char_file):
            continue
        for file in route.get("stable_files", []):
            stable_by_file.setdefault(file, []).append(route["oracle_id"])

    rows = []
    for candidate in read_csv(args.candidate_csv):
        file = candidate["file"]
        oracle_ids = stable_by_file.get(file, [])
        if oracle_ids:
            status = "stable"
            reason = "Candidate file is covered by a passing route-level characterization."
        elif candidate["candidate_type"] in review_types and candidate.get("dom_selectors"):
            status = "needs_review"
            reason = "Rendered-output candidate requires manual route mapping."
        else:
            status = "pending"
            reason = "No passing route-level oracle mapped."
        rows.append(
            {
                "candidate_id": candidate["candidate_id"],
                "project": candidate["project"],
                "file": file,
                "candidate_type": candidate["candidate_type"],
                "oracle_status": status,
                "oracle_ids": ";".join(oracle_ids),
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
