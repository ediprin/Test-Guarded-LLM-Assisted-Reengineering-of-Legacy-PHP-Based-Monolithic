#!/usr/bin/env python3
"""Pre-treatment testability screening for extracted candidates.

This script combines candidate evidence with available gate artifacts and emits
screening labels. It does not mark candidates eligible unless an oracle has
already been validated. Without oracle logs, candidates remain pending.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


FIELDS = [
    "candidate_id",
    "project",
    "file",
    "candidate_type",
    "syntax_status",
    "oracle_status",
    "screening_status",
    "screening_reason",
]


def load_syntax(path: Path | None) -> dict[str, str]:
    if not path or not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as handle:
        return {row["file"]: row["status"] for row in csv.DictReader(handle)}


def has_web_contract(row: dict[str, str]) -> bool:
    return bool(row.get("request_parameters") or row.get("dom_selectors") or row.get("forms"))


def classify(row: dict[str, str], syntax_status: str) -> tuple[str, str]:
    if syntax_status == "FAIL":
        return (
            "PENDING_TARGET_PHP_SYNTAX",
            "Failed syntax gate under current PHP CLI; rerun under subject target PHP before exclusion.",
        )

    if row.get("oracle_status") == "stable":
        return "ELIGIBLE", "Stable pre-transformation oracle recorded."

    if has_web_contract(row):
        return (
            "NEEDS_CHARACTERIZATION",
            "Candidate has observable request/output contract but no stable oracle yet.",
        )

    return (
        "NEEDS_MANUAL_ORACLE_REVIEW",
        "No obvious web contract was extracted; existing tests or manual characterization must be mapped.",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Screen extracted candidates before treatment.")
    parser.add_argument("--candidate-csv", required=True, type=Path)
    parser.add_argument("--syntax-csv", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    syntax = load_syntax(args.syntax_csv)
    rows = []
    with args.candidate_csv.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            syntax_status = syntax.get(row["file"], "NOT_RUN")
            status, reason = classify(row, syntax_status)
            rows.append(
                {
                    "candidate_id": row["candidate_id"],
                    "project": row["project"],
                    "file": row["file"],
                    "candidate_type": row["candidate_type"],
                    "syntax_status": syntax_status,
                    "oracle_status": row.get("oracle_status", "pending"),
                    "screening_status": status,
                    "screening_reason": reason,
                }
            )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["screening_status"]] = counts.get(row["screening_status"], 0) + 1
    print(f"Wrote {args.out}")
    for key, value in sorted(counts.items()):
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
