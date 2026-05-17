#!/usr/bin/env python3
"""Create treatment run packages for locked eligible candidates.

This prepares auditable experiment inputs without fabricating LLM outputs.
T1/T3 receive prompts. T2 receives conservative rule/static-only decisions.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


TREATMENTS = ["T1-llm-only", "T2-rule-static-only", "T3-evidence-llm"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_region(subject_dir: Path, rel_file: str, start: int, end: int) -> str:
    lines = (subject_dir / rel_file).read_text(encoding="utf-8", errors="ignore").splitlines()
    return "\n".join(lines[start - 1 : end]) + "\n"


def read_evidence(project: str, candidate_id: str) -> dict:
    path = Path("results") / "subjects" / project / "evidence" / f"{candidate_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def t1_prompt(candidate: dict[str, str], code: str) -> str:
    return f"""You are assisting with bounded reengineering of a legacy PHP-based monolithic web application.

Task:
Improve maintainability of the selected PHP code region while preserving observable behavior.

Candidate:
- Candidate ID: {candidate['candidate_id']}
- Project: {candidate['project']}
- File: {candidate['file']}
- Lines: {candidate['start_line']}-{candidate['end_line']}
- Candidate type: {candidate['candidate_type']}

Rules:
- Return a unified diff only.
- Do not change public routes, request parameters, session keys, database table names, DOM selectors, or form field names.
- Do not migrate framework, architecture, database schema, or application structure.
- Keep the change local and bounded.

Code region:
```php
{code}```
"""


def t3_prompt(candidate: dict[str, str], evidence: dict, code: str) -> str:
    return f"""You are assisting with test-guarded bounded reengineering of a legacy PHP-based monolithic web application.

Use the static-analysis evidence and preservation constraints below. Produce a minimal unified diff.

Candidate metadata:
- Candidate ID: {candidate['candidate_id']}
- Project: {candidate['project']}
- File: {candidate['file']}
- Lines: {candidate['start_line']}-{candidate['end_line']}
- Candidate type: {candidate['candidate_type']}
- Oracle IDs: {candidate['oracle_ids']}

Evidence schema:
```json
{json.dumps(evidence, indent=2)}
```

Constraints:
- Preserve all request parameters, session keys, database tables, forms, DOM selectors, and route behavior listed in the evidence.
- Use only allowed transformations from the evidence.
- Do not introduce new dependencies.
- Do not perform framework migration, database migration, or rewrite.
- Return a unified diff only.

Code region:
```php
{code}```
"""


def t2_decision(candidate: dict[str, str], evidence: dict) -> dict:
    ctype = candidate["candidate_type"]
    # Conservative baseline: only simple local identifier/dead-code rules are supported.
    # The current eligible set contains broader transformations, so most are not applicable.
    supported_types = {"dead_code", "local_identifier"}
    if ctype not in supported_types:
        return {
            "treatment": "T2-rule-static-only",
            "candidate_id": candidate["candidate_id"],
            "status": "not_applicable",
            "reason": f"No safe mechanical rule is implemented for candidate_type={ctype}.",
            "patch_generated": False,
        }
    return {
        "treatment": "T2-rule-static-only",
        "candidate_id": candidate["candidate_id"],
        "status": "supported_pending_rule_implementation",
        "reason": "Candidate type is mechanically transformable, but no matching concrete rule fired.",
        "patch_generated": False,
    }


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create treatment run packages.")
    parser.add_argument("--eligible-csv", default="results/summary/eligible_candidates_current.csv", type=Path)
    parser.add_argument("--subjects-dir", default="subjects", type=Path)
    parser.add_argument("--out-dir", default="runs", type=Path)
    parser.add_argument("--summary-out", default="results/summary/treatment_readiness.csv", type=Path)
    args = parser.parse_args()

    rows = []
    for candidate in read_csv(args.eligible_csv):
        project = candidate["project"]
        candidate_id = candidate["candidate_id"]
        run_dir = args.out_dir / project / candidate_id
        run_dir.mkdir(parents=True, exist_ok=True)

        evidence = read_evidence(project, candidate_id)
        code = read_region(
            args.subjects_dir / project,
            candidate["file"],
            int(candidate["start_line"]),
            int(candidate["end_line"]),
        )

        write_json(run_dir / "candidate.json", candidate)
        write_json(run_dir / "evidence.json", evidence)
        (run_dir / "code_region.php").write_text(code, encoding="utf-8")

        t1_dir = run_dir / "T1-llm-only"
        t1_dir.mkdir(exist_ok=True)
        (t1_dir / "prompt.md").write_text(t1_prompt(candidate, code), encoding="utf-8")
        write_json(t1_dir / "status.json", {"status": "pending_model_execution", "patch_generated": False})

        t2_dir = run_dir / "T2-rule-static-only"
        t2_dir.mkdir(exist_ok=True)
        decision = t2_decision(candidate, evidence)
        write_json(t2_dir / "decision.json", decision)
        (t2_dir / "patch.diff").write_text("", encoding="utf-8")

        t3_dir = run_dir / "T3-evidence-llm"
        t3_dir.mkdir(exist_ok=True)
        (t3_dir / "prompt.md").write_text(t3_prompt(candidate, evidence, code), encoding="utf-8")
        write_json(t3_dir / "status.json", {"status": "pending_model_execution", "patch_generated": False})

        rows.extend(
            [
                {
                    "candidate_id": candidate_id,
                    "project": project,
                    "treatment": "T1-llm-only",
                    "status": "pending_model_execution",
                    "patch_generated": "false",
                },
                {
                    "candidate_id": candidate_id,
                    "project": project,
                    "treatment": "T2-rule-static-only",
                    "status": decision["status"],
                    "patch_generated": str(decision["patch_generated"]).lower(),
                },
                {
                    "candidate_id": candidate_id,
                    "project": project,
                    "treatment": "T3-evidence-llm",
                    "status": "pending_model_execution",
                    "patch_generated": "false",
                },
            ]
        )

    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    with args.summary_out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["candidate_id", "project", "treatment", "status", "patch_generated"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote treatment packages for {len(read_csv(args.eligible_csv))} candidates to {args.out_dir}")
    print(f"Wrote {args.summary_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
