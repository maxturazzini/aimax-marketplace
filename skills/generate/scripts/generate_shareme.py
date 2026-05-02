#!/usr/bin/env python3
"""Generate a SHAREME.md draft from an analysis JSON file produced by
analyze_skill.py, using TEMPLATE.md as the structural source of truth.

The output is a starting point. Claude (or the human user) is expected to
review and fill in the prose-heavy sections (capabilities, alternative
use cases, onboarding questions tailored to the skill's domain).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def group_by_value(findings: list[dict]) -> dict[str, list[dict]]:
    grouped = defaultdict(list)
    for f in findings:
        grouped[f["value"]].append(f)
    return grouped


def build_author_specific_table(analysis: dict) -> str:
    paths = analysis.get("author_specific_paths", [])
    if not paths:
        return "| none | — | — | — |\n\n*This skill has no detected author-specific paths. Verify manually before publishing.*"

    grouped = group_by_value(paths)
    rows = []
    for value, occurrences in sorted(grouped.items()):
        first = occurrences[0]
        locations = ", ".join(
            f"{o['file']}:{o['line']}" for o in occurrences[:3]
        )
        if len(occurrences) > 3:
            locations += f" (+{len(occurrences) - 3} more)"
        kind = first["kind"].replace("_", " ")
        rows.append(
            f"| `{value}` | {locations} | author-specific {kind} | "
            f"replace with your equivalent or parametrize as `${{PLACEHOLDER}}` |"
        )
    return "\n".join(rows)


def build_behind_the_scenes(analysis: dict) -> str:
    network = analysis.get("network_indicators", [])
    fs_writes = analysis.get("filesystem_write_indicators", [])
    tools = analysis.get("external_tools", [])
    mcp = analysis.get("mcp_servers", [])

    lines = []

    if network:
        domains = sorted({
            f["value"].split("/")[2] for f in network
            if f["value"].startswith("http")
            and len(f["value"].split("/")) > 2
        })
        if domains:
            lines.append(f"- **Network calls**: detected references to {', '.join(domains)}")
        else:
            n = len(network)
            noun = "indicator" if n == 1 else "indicators"
            lines.append(f"- **Network calls**: {n} {noun} detected — review the code to confirm")
    else:
        lines.append("- **Network calls**: none detected (verify manually)")

    if fs_writes:
        files_with_writes = sorted({f["file"] for f in fs_writes})
        lines.append(f"- **File system writes**: detected in {len(files_with_writes)} file(s) — review paths in {', '.join(files_with_writes[:3])}")
    else:
        lines.append("- **File system writes**: none detected (verify manually)")

    if mcp:
        lines.append(f"- **MCP servers used**: {', '.join(mcp)}")
    else:
        lines.append("- **MCP servers used**: none detected")

    if tools:
        lines.append(f"- **External tools**: {', '.join(tools)}")
    else:
        lines.append("- **External tools**: none detected")

    lines.append("- **Persistent state**: review the skill manually for browser profiles, caches, or databases")

    return "\n".join(lines)


def build_prerequisites(analysis: dict) -> str:
    deps = analysis.get("python_dependencies", [])
    tools = analysis.get("external_tools", [])

    lines = []
    if deps:
        lines.append(f"- **Python dependencies**: `{', '.join(deps)}`")
    else:
        lines.append("- **Python dependencies**: none detected")

    if tools:
        lines.append(f"- **System tools**: {', '.join(tools)}")

    lines.append("- **Runtime**: review the skill code to confirm Python version and OS expectations")
    lines.append("- **Accounts and tokens**: review the skill code for API keys, credentials, login flows")

    return "\n".join(lines)


def render_shareme(analysis: dict, template: str) -> str:
    skill_name = analysis["skill_name"]
    metadata = analysis.get("metadata", {})
    description = metadata.get("description", "<TODO: one or two lines describing the skill>")

    output = template.replace("`<skill-name>`", f"`{skill_name}`")

    output = output.replace(
        "<One or two lines. What this skill actually does.>",
        description,
    )

    output = output.replace(
        "| `<element>` | `<file:line or path>` | <reason author chose this value> | <what to replace it with> |\n| `<element>` | `<file:line or path>` | <reason> | <how to adapt> |",
        build_author_specific_table(analysis),
    )

    behind_the_scenes_block = (
        "- **Network calls**: <none, or list domains/endpoints>\n"
        "- **File system writes**: <inside skill folder only, or list paths outside>\n"
        "- **External services**: <none, or list APIs / MCP servers / OS integrations>\n"
        "- **Persistent state**: <none, or describe browser profiles, caches, databases>\n"
        "- **Tools used**: <list shell commands, binaries, system tools>"
    )
    output = output.replace(behind_the_scenes_block, build_behind_the_scenes(analysis))

    prerequisites_block = (
        "- **Runtime**: <Python 3.x, Node X, etc.>\n"
        "- **OS**: <macOS / Linux / Windows / cross-platform>\n"
        "- **Dependencies**: <list, with versions if relevant>\n"
        "- **OS permissions**: <e.g., screen recording, accessibility>\n"
        "- **Accounts and tokens**: <list services and what kind of access>"
    )
    output = output.replace(prerequisites_block, build_prerequisites(analysis))

    header = (
        f"<!-- Generated by /shareme:generate. "
        f"Review every section before sharing. "
        f"Sections marked with <TODO: ...> require human input. -->\n\n"
    )
    return header + output


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a SHAREME.md from an analysis JSON.",
    )
    parser.add_argument(
        "--analysis",
        required=True,
        help="Path to JSON file produced by analyze_skill.py",
    )
    parser.add_argument(
        "--template",
        required=True,
        help="Path to TEMPLATE.md (typically ../../TEMPLATE.md from the skill)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Destination path for the generated SHAREME.md",
    )
    args = parser.parse_args()

    analysis_path = Path(args.analysis).expanduser().resolve()
    template_path = Path(args.template).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    if not analysis_path.exists():
        print(f"error: analysis file not found: {analysis_path}", file=sys.stderr)
        return 2
    if not template_path.exists():
        print(f"error: template file not found: {template_path}", file=sys.stderr)
        return 2

    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    template = template_path.read_text(encoding="utf-8")

    shareme = render_shareme(analysis, template)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(shareme, encoding="utf-8")
    print(f"SHAREME.md written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
