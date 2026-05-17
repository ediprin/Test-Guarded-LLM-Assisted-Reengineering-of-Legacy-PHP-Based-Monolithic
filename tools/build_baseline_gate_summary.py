#!/usr/bin/env python3
"""Build baseline gate summary for locked eligible candidates."""

from __future__ import annotations

import csv
import json
from pathlib import Path


FIELDS = [
    "candidate_id",
    "project",
    "file",
    "candidate_type",
    "syntax_status",
    "oracle_status",
    "baseline_gate_status",
    "oracle_ids",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def syntax_map(project: str) -> dict[str, str]:
    syntax_dir = Path("results") / "subjects" / project / "syntax"
    path = syntax_dir / ("syntax_php72_generic.csv" if project == "kanboard" else "syntax_php56_generic.csv")
    return {row["file"]: row["status"] for row in read_csv(path)}


def main() -> int:
    eligible = read_csv(Path("results") / "summary" / "eligible_candidates_current.csv")
    syntax_by_project = {project: syntax_map(project) for project in sorted({row["project"] for row in eligible})}
    rows = []
    for row in eligible:
        syntax_status = syntax_by_project[row["project"]].get(row["file"], "NOT_RUN")
        oracle_status = "PASS" if row.get("oracle_ids") else "FAIL"
        baseline = "PASS" if syntax_status == "PASS" and oracle_status == "PASS" else "FAIL"
        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "project": row["project"],
                "file": row["file"],
                "candidate_type": row["candidate_type"],
                "syntax_status": syntax_status,
                "oracle_status": oracle_status,
                "baseline_gate_status": baseline,
                "oracle_ids": row.get("oracle_ids", ""),
            }
        )

    out = Path("results") / "summary" / "baseline_gate_summary_current.csv"
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    passes = sum(1 for row in rows if row["baseline_gate_status"] == "PASS")
    print(f"Wrote {out}: {passes}/{len(rows)} baseline pass")
    return 0 if passes == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
