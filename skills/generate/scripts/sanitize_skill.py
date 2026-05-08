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


def copy_skill(source: Path, target: Path, exclude_globs: list[str]) -> None:
    if target.exists():
        raise FileExistsError(f"target already exists: {target}")
    ignore_patterns = list(exclude_globs) + [
        "__pycache__", ".pytest_cache", ".venv", "venv", "*.pyc",
    ]
    shutil.copytree(source, target, ignore=shutil.ignore_patterns(*ignore_patterns))


def apply_text_replacements(file_path: Path, replacements: list[tuple[str, str]]) -> int:
    """Replace literal strings inside a file. Returns number of files touched."""
    if not replacements:
        return 0
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return 0
    original = content
    # Sort by descending length so longer keys win (e.g., "Massimiliano" before "Massimi").
    for key, value in sorted(replacements, key=lambda r: -len(r[0])):
        if not key:
            continue
        content = content.replace(key, value)
    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return 1
    return 0


def sanitize(
    source: Path,
    target: Path,
    analysis: dict,
    do_replace: bool,
    rename_to: str | None,
    text_replacements: list[tuple[str, str]],
    exclude_globs: list[str],
) -> None:
    copy_skill(source, target, exclude_globs)

    # Rename references to the original skill folder name inside content.
    # Touches frontmatter `name:` and inline path references like
    # `.claude/skills/<old-name>/...`.
    original_skill_name = analysis.get("skill_name") or source.name
    rename_replacements: list[tuple[str, str]] = []
    if rename_to and rename_to != original_skill_name:
        rename_replacements.append((original_skill_name, rename_to))

    all_text_replacements = rename_replacements + list(text_replacements)

    if all_text_replacements:
        for path in target.rglob("*"):
            if not path.is_file():
                continue
            ext = path.suffix.lower()
            if ext and ext not in COMMENT_BY_EXT and ext not in {
                ".txt", ".yaml", ".yml", ".json", ".toml", ".cfg", ".ini",
            }:
                continue
            apply_text_replacements(path, all_text_replacements)

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

    # Surface proper-noun candidates as TODO_ADAPT markers at first occurrence,
    # so the adopter sees them even if they did not pass --replace.
    for candidate in analysis.get("proper_noun_candidates", []):
        token = candidate["token"]
        # Skip if the user already provided a replacement for this token.
        if any(key == token for key, _ in text_replacements):
            continue
        first = candidate.get("first_occurrence") or {}
        rel_file = first.get("file")
        line_no = first.get("line")
        if not rel_file or not line_no:
            continue
        copied = target / rel_file
        if not copied.exists():
            continue
        insert_markers(copied, [
            (line_no, f"proper-noun candidate '{token}' appears {candidate['count']}x — confirm before sharing"),
        ])


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
    parser.add_argument(
        "--rename-to",
        help="Rename the skill: replace original folder name with this string in all text content (frontmatter, paths). The target folder name still comes from the `target` argument.",
    )
    parser.add_argument(
        "--replace",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Literal string replacement applied to all text files. Repeat the flag for multiple replacements (e.g. --replace Max=Utente --replace Massimiliano=l'utente).",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="Skip files matching this glob when copying (e.g. --exclude '7-*.md'). Repeatable.",
    )
    args = parser.parse_args()

    text_replacements: list[tuple[str, str]] = []
    for item in args.replace:
        if "=" not in item:
            print(f"error: --replace expects KEY=VALUE, got: {item}", file=sys.stderr)
            return 2
        key, _, value = item.partition("=")
        text_replacements.append((key, value))

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
        sanitize(
            source,
            target,
            analysis,
            args.sanitize,
            rename_to=args.rename_to,
            text_replacements=text_replacements,
            exclude_globs=args.exclude,
        )
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
