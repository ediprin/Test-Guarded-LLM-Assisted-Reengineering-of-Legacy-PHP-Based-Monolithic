#!/usr/bin/env python3
"""Build paper-ready tables from the organized experiment artifacts."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Iterable


SUBJECTS = [
    "dokuwiki",
    "kanboard",
]

TYPE_FIELDS = [
    "long_method_or_region",
    "mixed_php_html",
    "sql_data_access",
    "session_dependent_logic",
    "form_handling",
    "mixed_php_html_sql",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def subject_dir(subject: str) -> Path:
    return Path("results") / "subjects" / subject


def candidate_rows(subject: str) -> list[dict[str, str]]:
    return read_csv(subject_dir(subject) / "candidates" / "candidates.csv")


def screening_rows(subject: str) -> list[dict[str, str]]:
    return read_csv(subject_dir(subject) / "screening" / "screening.csv")


def syntax_rows(subject: str) -> list[dict[str, str]]:
    syntax_dir = subject_dir(subject) / "syntax"
    if subject == "kanboard" and (syntax_dir / "syntax_php72_generic.csv").exists():
        return read_csv(syntax_dir / "syntax_php72_generic.csv")
    if (syntax_dir / "syntax_php56_generic.csv").exists():
        return read_csv(syntax_dir / "syntax_php56_generic.csv")
    if (syntax_dir / "syntax_php56_compose.csv").exists():
        return read_csv(syntax_dir / "syntax_php56_compose.csv")
    return []


def oracle_counts(subject: str) -> Counter:
    counts: Counter[str] = Counter()
    oracle_dir = subject_dir(subject) / "oracle"
    preferred = oracle_dir / "coverage.csv"
    paths = [preferred] if preferred.exists() else list(oracle_dir.glob("*.csv"))
    for path in paths:
        for row in read_csv(path):
            counts[row.get("oracle_status", "unknown")] += 1
    return counts


def characterization_status(subject: str) -> str:
    char_dir = subject_dir(subject) / "characterization"
    statuses = [row.get("status", "") for path in char_dir.glob("*.csv") for row in read_csv(path)]
    if not statuses:
        return "not_restored"
    if all(status == "PASS" for status in statuses):
        return "pass"
    return "partial_or_fail"


def build_subject_audit(out_dir: Path) -> None:
    rows = read_csv(Path("results") / "summary" / "audit_matrix.csv")
    fields = [
        "project",
        "selected_tag",
        "commit",
        "php_version",
        "db_required",
        "install_status",
        "test_command",
        "static_tools_status",
        "candidate_count",
    ]
    write_csv(out_dir / "table_1_subject_audit.csv", fields, ({field: row.get(field, "") for field in fields} for row in rows))


def build_candidate_distribution(out_dir: Path) -> None:
    fields = ["project", "initial_candidates"] + TYPE_FIELDS
    rows: list[dict[str, object]] = []
    total = Counter()
    total_candidates = 0
    for subject in SUBJECTS:
        candidates = candidate_rows(subject)
        counts = Counter(row["candidate_type"] for row in candidates)
        total.update(counts)
        total_candidates += len(candidates)
        row: dict[str, object] = {"project": subject, "initial_candidates": len(candidates)}
        for field in TYPE_FIELDS:
            row[field] = counts.get(field, 0)
        rows.append(row)
    total_row: dict[str, object] = {"project": "TOTAL", "initial_candidates": total_candidates}
    for field in TYPE_FIELDS:
        total_row[field] = total.get(field, 0)
    rows.append(total_row)
    write_csv(out_dir / "table_2_candidate_distribution.csv", fields, rows)


def build_syntax_summary(out_dir: Path) -> None:
    fields = ["project", "candidate_files", "syntax_pass", "syntax_fail", "php_version", "image"]
    rows: list[dict[str, object]] = []
    for subject in SUBJECTS:
        rows_in = syntax_rows(subject)
        pass_count = sum(1 for row in rows_in if row.get("status") == "PASS")
        fail_count = len(rows_in) - pass_count
        rows.append(
            {
                "project": subject,
                "candidate_files": len(rows_in),
                "syntax_pass": pass_count,
                "syntax_fail": fail_count,
                "php_version": rows_in[0].get("php_version", "") if rows_in else "",
                "image": rows_in[0].get("image", "") if rows_in and "image" in rows_in[0] else "compose",
            }
        )
    write_csv(out_dir / "table_3_target_syntax_gate.csv", fields, rows)


def build_screening_summary(out_dir: Path) -> None:
    fields = [
        "project",
        "initial_candidates",
        "needs_characterization",
        "needs_manual_oracle_review",
        "pending_target_php_syntax",
        "eligible",
    ]
    rows: list[dict[str, object]] = []
    for subject in SUBJECTS:
        screening = screening_rows(subject)
        counts = Counter(row.get("screening_status", "") for row in screening)
        rows.append(
            {
                "project": subject,
                "initial_candidates": len(screening),
                "needs_characterization": counts.get("NEEDS_CHARACTERIZATION", 0),
                "needs_manual_oracle_review": counts.get("NEEDS_MANUAL_ORACLE_REVIEW", 0),
                "pending_target_php_syntax": counts.get("PENDING_TARGET_PHP_SYNTAX", 0),
                "eligible": counts.get("ELIGIBLE", 0),
            }
        )
    write_csv(out_dir / "table_4_testability_screening.csv", fields, rows)


def build_runtime_oracle(out_dir: Path) -> None:
    fields = ["project", "runtime_characterization", "oracle_stable", "oracle_needs_review", "oracle_pending"]
    rows: list[dict[str, object]] = []
    for subject in SUBJECTS:
        counts = oracle_counts(subject)
        rows.append(
            {
                "project": subject,
                "runtime_characterization": characterization_status(subject),
                "oracle_stable": counts.get("stable", 0),
                "oracle_needs_review": counts.get("needs_review", 0),
                "oracle_pending": counts.get("pending", 0),
            }
        )
    write_csv(out_dir / "table_5_runtime_oracle_coverage.csv", fields, rows)


def build_totals(out_dir: Path) -> None:
    candidates = sum(len(candidate_rows(subject)) for subject in SUBJECTS)
    evidence_files = sum(len(list((subject_dir(subject) / "evidence").glob("*.json"))) for subject in SUBJECTS)
    syntax_files = sum(len(syntax_rows(subject)) for subject in SUBJECTS)
    syntax_fail = sum(1 for subject in SUBJECTS for row in syntax_rows(subject) if row.get("status") != "PASS")
    stable_oracles = sum(oracle_counts(subject).get("stable", 0) for subject in SUBJECTS)
    eligible_current = read_csv(Path("results") / "summary" / "eligible_candidates_current.csv")
    rows = [
        {"metric": "subject_systems", "value": len(SUBJECTS)},
        {"metric": "initial_candidates", "value": candidates},
        {"metric": "evidence_json_files", "value": evidence_files},
        {"metric": "candidate_bearing_files_syntax_checked", "value": syntax_files},
        {"metric": "target_runtime_syntax_failures", "value": syntax_fail},
        {"metric": "currently_mapped_stable_oracles", "value": stable_oracles},
        {"metric": "locked_eligible_candidates_current", "value": len(eligible_current)},
    ]
    write_csv(out_dir / "table_0_dataset_totals.csv", ["metric", "value"], rows)


def main() -> int:
    out_dir = Path("paper") / "tables"
    build_totals(out_dir)
    build_subject_audit(out_dir)
    build_candidate_distribution(out_dir)
    build_syntax_summary(out_dir)
    build_screening_summary(out_dir)
    build_runtime_oracle(out_dir)
    print(f"Wrote paper tables to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
