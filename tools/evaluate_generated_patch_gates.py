#!/usr/bin/env python3
"""Evaluate generated treatment patches with local gates.

The gate is intentionally conservative and reproducible:
- apply the generated patch in an isolated sparse workspace,
- run target-runtime `php -l` through Docker for changed PHP files,
- compute simple before/after static proxies on the candidate file.

This script does not mutate `subjects/*`.
"""

from __future__ import annotations

import csv
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
    "syntax_status",
    "syntax_message",
    "candidate_loc_before",
    "candidate_loc_after",
    "candidate_complexity_before",
    "candidate_complexity_after",
    "loc_delta",
    "complexity_delta",
    "static_proxy_status",
    "gate_outcome",
    "workspace",
]

PHP_IMAGES = {
    "dokuwiki": "php:5.6-cli",
    "kanboard": "php:7.2-cli",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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


def codex_targets(patch: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"\*\*\* Update File: (.+)", patch)]


def unified_targets(patch: str) -> list[str]:
    targets: list[str] = []
    for line in patch.splitlines():
        if line.startswith("+++ b/"):
            targets.append(line[6:].strip())
        elif line.startswith("+++ "):
            target = line[4:].strip()
            if target != "/dev/null":
                targets.append(target.replace("b/", "", 1))
    return targets


def patch_targets(patch: str, fmt: str) -> list[str]:
    if fmt == "codex_apply_patch":
        return codex_targets(patch)
    if fmt == "unified_diff":
        return unified_targets(patch)
    return []


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
    sections = re.split(r"\n@@(?: .*)?\n", "\n" + body)
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


def copy_sparse_subject(project: str, targets: set[str], workspace: Path) -> tuple[bool, str]:
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    missing: list[str] = []
    for rel in sorted(targets):
        src = Path("subjects") / project / rel
        dst = workspace / rel
        if not src.exists():
            missing.append(rel)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    if missing:
        return False, "missing_targets:" + ";".join(missing)
    return True, ""


def candidate_rows() -> dict[str, dict[str, str]]:
    return {row["candidate_id"]: row for row in read_csv(Path("results/summary/eligible_candidates_current.csv"))}


def generated_rows() -> list[dict[str, str]]:
    rows = []
    for row in read_csv(Path("results/summary/treatment_outputs_summary.csv")):
        if row["treatment"] == "T2-rule-static-only":
            continue
        if row["patch_generated"] == "true":
            rows.append(row)
    return rows


def simple_metrics(text: str) -> tuple[int, int]:
    loc = sum(1 for line in text.splitlines() if line.strip())
    complexity_pattern = re.compile(r"\b(if|elseif|for|foreach|while|case|catch|switch)\b|&&|\|\|")
    complexity = len(complexity_pattern.findall(text))
    return loc, complexity


def syntax_check(project: str, workspace: Path, files: list[str]) -> tuple[str, str]:
    image = PHP_IMAGES.get(project)
    if not image:
        return "SKIP", "no_php_image"
    php_files = [rel for rel in files if rel.lower().endswith(".php")]
    if not php_files:
        return "PASS", "no_php_files_changed"
    messages = []
    for rel in php_files:
        code, out = run(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{workspace.resolve()}:/work",
                image,
                "php",
                "-l",
                "/work/" + rel.replace("\\", "/"),
            ],
            timeout=120,
        )
        messages.append(f"{rel}: {out}")
        if code != 0:
            return "FAIL", " | ".join(messages)
    return "PASS", " | ".join(messages)


def main() -> int:
    candidates = candidate_rows()
    out_rows = []
    for row in generated_rows():
        candidate = candidates[row["candidate_id"]]
        project = candidate["project"]
        candidate_file = candidate["file"]
        patch_path = Path("runs") / project / candidate["candidate_id"] / row["treatment"] / "patch.diff"
        patch = patch_path.read_text(encoding="utf-8", errors="ignore")
        fmt = detect_format(patch)
        targets = set(patch_targets(patch, fmt))
        targets.add(candidate_file)
        workspace = Path("workspaces") / "patch_gate" / project / candidate["candidate_id"] / row["treatment"]

        before_text = (Path("subjects") / project / candidate_file).read_text(encoding="utf-8", errors="ignore")
        before_loc, before_complexity = simple_metrics(before_text)

        copied, copy_msg = copy_sparse_subject(project, targets, workspace)
        if not copied:
            apply_status, apply_msg = "apply_failed", copy_msg
        elif fmt == "unified_diff":
            code, out = run(["git", "apply", "--whitespace=nowarn", str(patch_path.resolve())], cwd=workspace)
            apply_status, apply_msg = ("applied", "") if code == 0 else ("apply_failed", out)
        elif fmt == "codex_apply_patch":
            apply_status, apply_msg = apply_codex(workspace, patch)
        else:
            apply_status, apply_msg = "apply_failed", f"unsupported_format:{fmt}"

        syntax_status, syntax_message = "SKIP", apply_msg
        after_loc, after_complexity = before_loc, before_complexity
        if apply_status == "applied":
            after_path = workspace / candidate_file
            after_text = after_path.read_text(encoding="utf-8", errors="ignore")
            after_loc, after_complexity = simple_metrics(after_text)
            syntax_status, syntax_message = syntax_check(project, workspace, sorted(targets))

        loc_delta = after_loc - before_loc
        complexity_delta = after_complexity - before_complexity
        if apply_status != "applied":
            static_status = "not_evaluated"
            outcome = "rejected_apply"
        elif syntax_status != "PASS":
            static_status = "not_evaluated"
            outcome = "rejected_syntax"
        elif complexity_delta < 0 or loc_delta < 0:
            static_status = "improved_proxy"
            outcome = "accepted_syntax_static_proxy_improved"
        elif complexity_delta == 0 and loc_delta == 0:
            static_status = "unchanged_proxy"
            outcome = "accepted_syntax_static_proxy_unchanged"
        elif complexity_delta <= 0:
            static_status = "non_worsening_complexity"
            outcome = "accepted_syntax_static_proxy_non_worsening"
        else:
            static_status = "worsened_proxy"
            outcome = "accepted_syntax_static_proxy_worsened"

        out_rows.append(
            {
                "candidate_id": candidate["candidate_id"],
                "project": project,
                "treatment": row["treatment"],
                "patch_format": fmt,
                "apply_status": apply_status,
                "syntax_status": syntax_status,
                "syntax_message": syntax_message,
                "candidate_loc_before": before_loc,
                "candidate_loc_after": after_loc,
                "candidate_complexity_before": before_complexity,
                "candidate_complexity_after": after_complexity,
                "loc_delta": loc_delta,
                "complexity_delta": complexity_delta,
                "static_proxy_status": static_status,
                "gate_outcome": outcome,
                "workspace": workspace.as_posix(),
            }
        )

    out = Path("results/summary/treatment_patch_gate_results.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"Wrote {out} ({len(out_rows)} generated patches evaluated)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
