#!/usr/bin/env python3
"""Apply generated pilot patches in isolated workspaces.

Supports conventional unified diffs via `git apply` and Codex apply-patch blocks
via a small parser for Update File hunks.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
from pathlib import Path


FIELDS = [
    "candidate_id",
    "project",
    "treatment",
    "patch_format",
    "apply_status",
    "workspace",
    "message",
]


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 120) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout.strip()


def detect_format(patch: str) -> str:
    stripped = patch.lstrip()
    if stripped.startswith("*** Begin Patch"):
        return "codex_apply_patch"
    if stripped.startswith("diff --git ") or stripped.startswith("--- "):
        return "unified_diff"
    if stripped:
        return "unknown"
    return "none"


def copy_subject(project: str, workspace: Path) -> None:
    if workspace.exists():
        shutil.rmtree(workspace)
    ignore = shutil.ignore_patterns(".git")
    shutil.copytree(Path("subjects") / project, workspace, ignore=ignore)
    run(["git", "init"], cwd=workspace)
    run(["git", "add", "-A"], cwd=workspace)
    run(["git", "commit", "-m", "baseline"], cwd=workspace)


def apply_unified(workspace: Path, patch_path: Path) -> tuple[str, str]:
    code, out = run(["git", "apply", "--whitespace=nowarn", str(patch_path.resolve())], cwd=workspace)
    return ("applied" if code == 0 else "apply_failed", out)


def parse_codex_patch(patch: str):
    blocks = re.split(r"\n(?=\*\*\* Update File: )", patch)
    for block in blocks:
        match = re.search(r"\*\*\* Update File: (.+)", block)
        if not match:
            continue
        rel = match.group(1).strip()
        body = block[match.end() :].strip()
        body = body.replace("*** End Patch", "").strip("\n")
        yield rel, body


def apply_update_body(original: str, body: str) -> str:
    text = original
    sections = re.split(r"\n@@\n", "\n" + body)
    for section in sections:
        section = section.strip("\n")
        if not section or section.startswith("***"):
            continue
        old_lines: list[str] = []
        new_lines: list[str] = []
        for line in section.splitlines():
            if line.startswith("-"):
                old_lines.append(line[1:])
            elif line.startswith("+"):
                new_lines.append(line[1:])
            elif line.startswith(" "):
                old_lines.append(line[1:])
                new_lines.append(line[1:])
            elif line.startswith("@@"):
                continue
        old = "\n".join(old_lines)
        new = "\n".join(new_lines)
        if old and old in text:
            text = text.replace(old, new, 1)
        else:
            raise ValueError("context_not_found")
    return text


def apply_codex(workspace: Path, patch: str) -> tuple[str, str]:
    try:
        any_block = False
        for rel, body in parse_codex_patch(patch):
            any_block = True
            target = workspace / rel
            if not target.exists():
                return "apply_failed", f"target_not_found:{rel}"
            original = target.read_text(encoding="utf-8", errors="ignore")
            updated = apply_update_body(original, body)
            target.write_text(updated, encoding="utf-8")
        if not any_block:
            return "apply_failed", "no_update_file_block"
        return "applied", ""
    except Exception as exc:
        return "apply_failed", str(exc)


def iter_generated(summary_path: Path):
    with summary_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["treatment"] == "T2-rule-static-only":
                continue
            if row["patch_generated"] != "true":
                continue
            yield row


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply generated pilot patches.")
    parser.add_argument("--summary", default="results/summary/treatment_outputs_summary.csv", type=Path)
    parser.add_argument("--out", default="results/summary/pilot_patch_application.csv", type=Path)
    parser.add_argument("--workspace-root", default="workspaces/pilot", type=Path)
    args = parser.parse_args()

    rows = []
    for row in iter_generated(args.summary):
        project = row["project"]
        candidate_id = row["candidate_id"]
        treatment = row["treatment"]
        patch_path = Path("runs") / project / candidate_id / treatment / "patch.diff"
        patch = patch_path.read_text(encoding="utf-8", errors="ignore")
        fmt = detect_format(patch)
        workspace = args.workspace_root / project / candidate_id / treatment
        copy_subject(project, workspace)
        if fmt == "unified_diff":
            status, msg = apply_unified(workspace, patch_path)
        elif fmt == "codex_apply_patch":
            status, msg = apply_codex(workspace, patch)
        else:
            status, msg = "apply_failed", f"unsupported_format:{fmt}"
        rows.append(
            {
                "candidate_id": candidate_id,
                "project": project,
                "treatment": treatment,
                "patch_format": fmt,
                "apply_status": status,
                "workspace": workspace.as_posix(),
                "message": msg,
            }
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {args.out} ({len(rows)} patch attempts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
