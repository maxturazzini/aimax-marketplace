#!/usr/bin/env python3
"""Analyze a Claude Code skill and emit structured JSON describing
its capabilities, dependencies, side effects, and author-specific bits.

Used by /shareme:wrap to feed generate_shareme.py and sanitize_skill.py.
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

# Capitalized tokens that are likely author-specific proper nouns when they
# appear with high frequency in prose (names, brand-prefixed identifiers).
# Detection is heuristic: we surface candidates, the skill prompt asks the
# user to confirm before sanitizing.
PROPER_NOUN_RE = re.compile(r"\b[A-Z][a-zàèéìòùA-Z]{2,}(?:\s+[A-Z][a-zàèéìòù]+)?\b")

# Tokens that look like proper nouns by capitalization but are common
# English/Italian words, project structure, or technical terms — never flag.
PROPER_NOUN_STOPWORDS = {
    "Claude", "Code", "Skill", "Skills", "Tool", "Tools", "Read", "Write",
    "Edit", "Bash", "Glob", "Grep", "Task", "Agent", "MCP", "API", "JSON",
    "YAML", "URL", "URLs", "HTTP", "HTTPS", "SQL", "HTML", "CSS", "PDF",
    "PDFs", "Python", "Node", "JavaScript", "TypeScript", "Markdown", "Git",
    "GitHub", "Linux", "MacOS", "Windows", "OneDrive", "iCloud", "Dropbox",
    "When", "If", "Use", "After", "Before", "STOP", "TODO", "FASE", "OBBLIGATORIO",
    "Nota", "Note", "Esempio", "Esempi", "Example", "Examples", "Output", "Input",
    "Path", "Paths", "File", "Files", "Folder", "Folders", "Directory", "Directories",
    "Quando", "Mai", "Sempre", "Vero", "Falso", "True", "False", "None",
    "Action", "Items", "Item", "Step", "Steps", "Phase", "Phases",
    "AskUserQuestion", "TodoWrite", "WebFetch", "WebSearch",
    "SHAREME", "SKILL", "TEMPLATE", "SPEC", "CONVENTIONS", "README", "LICENSE",
    "SE", "FERMARSI", "FERMARTI", "FORMAT", "DIVERSO", "DUBBI", "PRESENTI",
    # Common Italian words that often get capitalized at line/section starts.
    "Cose", "Fare", "Punti", "Aperti", "Punti Aperti", "Cosa", "Cose Fatte",
    "Tipologia", "Tipologie", "Cliente", "Clienti", "Progetto", "Progetti",
    "Nome", "Data", "Dopo", "Prima", "Sempre", "Mai", "Anche",
    "Introduzione", "Nuovo", "Nuova", "Nuovi", "Nuove",
    "Riunione", "Workshop", "Training", "Call", "Meeting", "Sessione",
    "Verbale", "Glossario", "Trascrizione",
    "Presenta", "Domande", "Risposte", "Conferma", "Procedere",
}

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


def detect_proper_noun_candidates(file_contents: dict[str, str], min_count: int = 3) -> list[dict]:
    """Find capitalized tokens that recur across the skill prose.
    Returns candidates with file occurrences for human review.
    Heuristic — meant for the orchestrator to ask the user about, not auto-replace.
    """
    counts: dict[str, list[tuple[str, int]]] = {}
    for rel, content in file_contents.items():
        for match in PROPER_NOUN_RE.finditer(content):
            token = match.group(0).strip()
            if token in PROPER_NOUN_STOPWORDS:
                continue
            # skip ALL-CAPS shorter than 4 chars (likely acronyms covered above)
            if token.isupper() and len(token) < 4:
                continue
            line_no = content[: match.start()].count("\n") + 1
            counts.setdefault(token, []).append((rel, line_no))

    candidates = []
    for token, occurrences in counts.items():
        if len(occurrences) >= min_count:
            candidates.append({
                "token": token,
                "count": len(occurrences),
                "files": sorted({o[0] for o in occurrences}),
                "first_occurrence": {"file": occurrences[0][0], "line": occurrences[0][1]},
            })
    candidates.sort(key=lambda c: -c["count"])
    return candidates


def detect_skill_name_references(skill_name: str, file_contents: dict[str, str]) -> list[dict]:
    """Find places where the skill folder name appears in content.
    These are renaming candidates when the adopter wants to rebrand the skill.
    """
    findings = []
    pattern = re.compile(re.escape(skill_name))
    for rel, content in file_contents.items():
        for match in pattern.finditer(content):
            line_no = content[: match.start()].count("\n") + 1
            findings.append({"file": rel, "line": line_no, "value": skill_name})
    return findings


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
    file_contents: dict[str, str] = {}

    for f in files:
        if not is_text_file(f):
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        rel = str(f.relative_to(skill_path))
        file_contents[rel] = content
        author_paths.extend(detect_author_paths(content, rel))
        network.extend(detect_network(content, rel))
        fs_writes.extend(detect_filesystem_writes(content, rel))
        tools.update(detect_external_tools(content, rel))
        mcp_servers.update(detect_mcp_servers(content))

    proper_noun_candidates = detect_proper_noun_candidates(file_contents)
    skill_name_refs = detect_skill_name_references(skill_path.name, file_contents)

    return {
        "skill_path": str(skill_path),
        "skill_name": skill_path.name,
        "metadata": extract_skill_metadata(skill_path),
        "files": relative_files,
        "author_specific_paths": author_paths,
        "proper_noun_candidates": proper_noun_candidates,
        "skill_name_references": skill_name_refs,
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
    print(f"skill-name references in content: {len(analysis['skill_name_references'])}")
    print(f"proper-noun candidates (>=3 occurrences): {len(analysis['proper_noun_candidates'])}")
    if analysis["proper_noun_candidates"]:
        top = ", ".join(f"{c['token']}({c['count']})" for c in analysis["proper_noun_candidates"][:5])
        print(f"  top: {top}")
    print(f"network indicators: {len(analysis['network_indicators'])}")
    print(f"filesystem-write indicators: {len(analysis['filesystem_write_indicators'])}")
    print(f"external tools: {', '.join(analysis['external_tools']) or 'none detected'}")
    print(f"mcp servers: {', '.join(analysis['mcp_servers']) or 'none detected'}")
    print(f"python deps: {', '.join(analysis['python_dependencies']) or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
