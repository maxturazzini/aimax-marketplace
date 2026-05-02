#!/usr/bin/env python3
"""Copy a skill folder into a sibling `<skill-name>_shared/` directory,
inserting `# TODO_ADAPT:` markers next to detected author-specific lines.
With `--sanitize`, also replaces detected author-specific paths with
`${PLACEHOLDER}` syntax.

Never modifies the original skill folder.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

COMMENT_BY_EXT = {
    ".py": "# ",
    ".sh": "# ",
    ".yaml": "# ",
    ".yml": "# ",
    ".toml": "# ",
    ".js": "// ",
    ".ts": "// ",
    ".json": None,  # JSON has no comments — skip marker insertion
    ".md": "<!-- ",
    ".html": "<!-- ",
    ".css": "/* ",
}

CLOSING_COMMENT = {
    ".md": " -->",
    ".html": " -->",
    ".css": " */",
}

PLACEHOLDER_BY_KIND = {
    "macos_user_home": "${USER_HOME}",
    "linux_user_home": "${USER_HOME}",
    "tilde_path": "${HOME_PATH}",
    "onedrive_path": "${CLOUD_STORAGE_PATH}",
    "icloud_path": "${CLOUD_STORAGE_PATH}",
    "dropbox_path": "${CLOUD_STORAGE_PATH}",
    "macos_cloudstorage": "${CLOUD_STORAGE_PATH}",
}


def comment_marker(file_path: Path, description: str) -> str | None:
    ext = file_path.suffix.lower()
    if ext not in COMMENT_BY_EXT or COMMENT_BY_EXT[ext] is None:
        return None
    open_c = COMMENT_BY_EXT[ext]
    close_c = CLOSING_COMMENT.get(ext, "")
    return f"{open_c}TODO_ADAPT: {description}{close_c}\n"


def insert_markers(file_path: Path, lines_to_mark: list[tuple[int, str]]) -> None:
    """Insert TODO_ADAPT markers above the specified lines.
    `lines_to_mark` is a list of (line_number_1based, description).
    """
    if not lines_to_mark:
        return

    try:
        original = file_path.read_text(encoding="utf-8")
    except Exception:
        return

    lines = original.splitlines(keepends=True)
    grouped: dict[int, list[str]] = defaultdict(list)
    for line_no, desc in lines_to_mark:
        grouped[line_no].append(desc)

    new_lines = []
    for idx, line in enumerate(lines, start=1):
        if idx in grouped:
            for desc in grouped[idx]:
                marker = comment_marker(file_path, desc)
                if marker:
                    indent = re.match(r"^(\s*)", line).group(1)
                    new_lines.append(f"{indent}{marker}")
        new_lines.append(line)

    file_path.write_text("".join(new_lines), encoding="utf-8")


def apply_placeholders(file_path: Path, paths: list[dict]) -> None:
    if not paths:
        return
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return

    replacements = sorted(
        {(p["value"], PLACEHOLDER_BY_KIND.get(p["kind"], "${AUTHOR_PATH}")) for p in paths},
        key=lambda x: -len(x[0]),
    )
    for original, placeholder in replacements:
        content = content.replace(original, placeholder)
    file_path.write_text(content, encoding="utf-8")


def copy_skill(source: Path, target: Path) -> None:
    if target.exists():
        raise FileExistsError(f"target already exists: {target}")
    shutil.copytree(source, target, ignore=shutil.ignore_patterns(
        "__pycache__", ".pytest_cache", ".venv", "venv", "*.pyc",
    ))


def sanitize(source: Path, target: Path, analysis: dict, do_replace: bool) -> None:
    copy_skill(source, target)

    paths = analysis.get("author_specific_paths", [])
    by_file: dict[str, list[dict]] = defaultdict(list)
    for p in paths:
        by_file[p["file"]].append(p)

    for rel_file, file_paths in by_file.items():
        copied = target / rel_file
        if not copied.exists():
            continue

        markers = [
            (p["line"], f"author-specific path detected: {p['value']}")
            for p in file_paths
        ]
        insert_markers(copied, markers)

        if do_replace:
            apply_placeholders(copied, file_paths)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Copy a skill into a sibling _shared/ folder with TODO_ADAPT markers.",
    )
    parser.add_argument(
        "skill_path",
        help="Path to the source skill folder",
    )
    parser.add_argument(
        "target",
        help="Destination folder (will be created, must not exist yet)",
    )
    parser.add_argument(
        "--analysis",
        required=True,
        help="Path to analysis JSON from analyze_skill.py",
    )
    parser.add_argument(
        "--sanitize",
        action="store_true",
        help="Also replace detected author-specific paths with ${PLACEHOLDER} syntax",
    )
    args = parser.parse_args()

    source = Path(args.skill_path).expanduser().resolve()
    target = Path(args.target).expanduser().resolve()
    analysis_path = Path(args.analysis).expanduser().resolve()

    if not source.is_dir():
        print(f"error: source is not a directory: {source}", file=sys.stderr)
        return 2
    if not analysis_path.exists():
        print(f"error: analysis file not found: {analysis_path}", file=sys.stderr)
        return 2

    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))

    try:
        sanitize(source, target, analysis, args.sanitize)
    except FileExistsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"sanitized copy written to {target}")
    if args.sanitize:
        print("placeholders applied; review every TODO_ADAPT marker before sharing")
    else:
        print("markers inserted; original values preserved (use --sanitize to apply placeholders)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
