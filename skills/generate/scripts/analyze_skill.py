#!/usr/bin/env python3
"""Analyze a Claude Code skill and emit structured JSON describing
its capabilities, dependencies, side effects, and author-specific bits.

Used by /shareme:generate to feed generate_shareme.py and sanitize_skill.py.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

PATH_PATTERNS = [
    (re.compile(r"/Users/([A-Za-z0-9._-]+)(/[^\s'\"`]*)?"), "macos_user_home"),
    (re.compile(r"/home/([A-Za-z0-9._-]+)(/[^\s'\"`]*)?"), "linux_user_home"),
    (re.compile(r"~/[^\s'\"`]+"), "tilde_path"),
    (re.compile(r"OneDrive[^\s'\"`]*", re.IGNORECASE), "onedrive_path"),
    (re.compile(r"iCloud[^\s'\"`]*", re.IGNORECASE), "icloud_path"),
    (re.compile(r"Dropbox[^\s'\"`]*", re.IGNORECASE), "dropbox_path"),
    (re.compile(r"Library/CloudStorage[^\s'\"`]*"), "macos_cloudstorage"),
]

NETWORK_PATTERNS = [
    re.compile(r"https?://[^\s'\"`)]+"),
    re.compile(r"\brequests\.(get|post|put|delete|patch)\b"),
    re.compile(r"\bhttpx\."),
    re.compile(r"\burllib\.request\b"),
    re.compile(r"\bfetch\("),
    re.compile(r"\bcurl\s+"),
]

FILESYSTEM_WRITE_PATTERNS = [
    re.compile(r"\bopen\([^)]+,\s*['\"]([wax])['\"]"),
    re.compile(r"\.write\("),
    re.compile(r"\.write_text\("),
    re.compile(r"\.write_bytes\("),
    re.compile(r"\bos\.makedirs\("),
    re.compile(r"\bPath\([^)]+\)\.mkdir\("),
    re.compile(r"\bshutil\.(copy|copytree|move)\b"),
]

EXTERNAL_TOOL_HINTS = [
    "ffmpeg", "ffprobe", "selenium", "playwright", "chromedriver",
    "git ", "gh ", "curl ", "wget ", "scp ", "ssh ", "docker ",
]

MCP_HINT = re.compile(r"mcp__[a-z0-9_]+", re.IGNORECASE)

SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".pytest_cache"}

TEXT_EXTENSIONS = {
    ".md", ".py", ".js", ".ts", ".sh", ".yaml", ".yml", ".json",
    ".txt", ".toml", ".ini", ".cfg", ".html", ".css", ".sql",
}


def is_text_file(path: Path) -> bool:
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    if path.name in {"requirements", "Dockerfile", "Makefile"}:
        return True
    return False


def walk_skill(skill_path: Path) -> list[Path]:
    files = []
    for root, dirs, filenames in os.walk(skill_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in filenames:
            p = Path(root) / fn
            files.append(p)
    return sorted(files)


def detect_author_paths(content: str, file_rel: str) -> list[dict]:
    findings = []
    for pattern, kind in PATH_PATTERNS:
        for match in pattern.finditer(content):
            value = match.group(0)
            line_no = content[: match.start()].count("\n") + 1
            findings.append({
                "kind": kind,
                "value": value,
                "file": file_rel,
                "line": line_no,
            })
    return findings


def detect_network(content: str, file_rel: str) -> list[dict]:
    findings = []
    for pattern in NETWORK_PATTERNS:
        for match in pattern.finditer(content):
            value = match.group(0)
            line_no = content[: match.start()].count("\n") + 1
            findings.append({
                "value": value,
                "file": file_rel,
                "line": line_no,
            })
    return findings


def detect_filesystem_writes(content: str, file_rel: str) -> list[dict]:
    findings = []
    for pattern in FILESYSTEM_WRITE_PATTERNS:
        for match in pattern.finditer(content):
            line_no = content[: match.start()].count("\n") + 1
            line_text = content.splitlines()[line_no - 1].strip() if content else ""
            findings.append({
                "match": match.group(0),
                "line_text": line_text[:200],
                "file": file_rel,
                "line": line_no,
            })
    return findings


def detect_external_tools(content: str, file_rel: str) -> list[str]:
    found = set()
    lower = content.lower()
    for hint in EXTERNAL_TOOL_HINTS:
        if hint in lower:
            found.add(hint.strip())
    return sorted(found)


def detect_mcp_servers(content: str) -> list[str]:
    return sorted(set(MCP_HINT.findall(content)))


def parse_requirements(skill_path: Path) -> list[str]:
    deps = []
    for req_file in skill_path.rglob("requirements.txt"):
        try:
            for line in req_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    deps.append(line)
        except Exception:
            pass
    return sorted(set(deps))


def extract_skill_metadata(skill_path: Path) -> dict:
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return {}
    content = skill_md.read_text(encoding="utf-8", errors="replace")
    meta = {}
    fm_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if fm_match:
        for line in fm_match.group(1).splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                meta[key.strip()] = value.strip()
    return meta


def analyze_skill(skill_path: Path) -> dict:
    if not skill_path.is_dir():
        raise ValueError(f"Not a directory: {skill_path}")

    files = walk_skill(skill_path)
    relative_files = [str(f.relative_to(skill_path)) for f in files]

    author_paths = []
    network = []
    fs_writes = []
    tools = set()
    mcp_servers = set()

    for f in files:
        if not is_text_file(f):
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        rel = str(f.relative_to(skill_path))
        author_paths.extend(detect_author_paths(content, rel))
        network.extend(detect_network(content, rel))
        fs_writes.extend(detect_filesystem_writes(content, rel))
        tools.update(detect_external_tools(content, rel))
        mcp_servers.update(detect_mcp_servers(content))

    return {
        "skill_path": str(skill_path),
        "skill_name": skill_path.name,
        "metadata": extract_skill_metadata(skill_path),
        "files": relative_files,
        "author_specific_paths": author_paths,
        "network_indicators": network,
        "filesystem_write_indicators": fs_writes,
        "external_tools": sorted(tools),
        "mcp_servers": sorted(mcp_servers),
        "python_dependencies": parse_requirements(skill_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze a Claude Code skill for SHAREME generation.",
    )
    parser.add_argument(
        "skill_path",
        help="Path to the skill folder (must contain SKILL.md)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON output (default: human-readable summary)",
    )
    parser.add_argument(
        "--output",
        help="Write JSON to this file instead of stdout (implies --json)",
    )
    args = parser.parse_args()

    skill_path = Path(args.skill_path).expanduser().resolve()
    try:
        analysis = analyze_skill(skill_path)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.output:
        Path(args.output).write_text(
            json.dumps(analysis, indent=2),
            encoding="utf-8",
        )
        print(f"analysis written to {args.output}")
        return 0

    if args.json:
        print(json.dumps(analysis, indent=2))
        return 0

    print(f"skill: {analysis['skill_name']}")
    print(f"files: {len(analysis['files'])}")
    print(f"author-specific path indicators: {len(analysis['author_specific_paths'])}")
    print(f"network indicators: {len(analysis['network_indicators'])}")
    print(f"filesystem-write indicators: {len(analysis['filesystem_write_indicators'])}")
    print(f"external tools: {', '.join(analysis['external_tools']) or 'none detected'}")
    print(f"mcp servers: {', '.join(analysis['mcp_servers']) or 'none detected'}")
    print(f"python deps: {', '.join(analysis['python_dependencies']) or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
