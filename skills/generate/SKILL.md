---
name: generate
description: Generates a SHAREME-compliant companion document for a Claude Code skill. Produces a sibling folder named `<skill-name>_shared/` containing a copy of the skill with `# TODO_ADAPT:` markers and a `SHAREME.md` following the standard at github.com/maxturazzini/shareme. Use this skill whenever the user wants to share, publish, distribute, or document a Claude Code skill they authored. Trigger keywords - "make this skill shareable", "generate SHAREME", "prepare skill for sharing", "document skill for adoption", "create companion doc", "/shareme:generate".
---

# /shareme:generate

Produce a SHAREME-compliant adoption package for any Claude Code skill.

## When to use this skill

- The user wants to share a skill with someone else
- The user wants to publish a skill to a public repo
- The user wants documentation that explains what a skill does and what it touches
- The user wants to audit their own skill for hidden author-specific bits

## What this skill does

Given a target skill (by name in `~/.claude/skills/` or by absolute path):

1. **Reads** every file in the target skill folder (SKILL.md, scripts, knowledge, references, prompts, assets)
2. **Analyzes** the skill to detect:
   - Hardcoded paths specific to the author (e.g., `/Users/{name}/`, OneDrive, iCloud paths)
   - Brand or product references that may need replacing
   - External dependencies (Python packages, OS tools, MCP servers, API endpoints)
   - Side effects (network calls, file writes outside the skill, persistent state)
   - Naming conventions tied to the author's project structure
3. **Produces** a sibling folder `<skill-name>_shared/` next to the original, containing:
   - A copy of the skill files
   - `# TODO_ADAPT:` markers placed at lines that need adopter attention
   - A generated `SHAREME.md` filled in based on the analysis, following [TEMPLATE.md](../../TEMPLATE.md) and [SPEC.md](../../SPEC.md)
4. **Never modifies** the original skill folder

## Triggers

- `/shareme:generate <skill-name>` — operates on `~/.claude/skills/<skill-name>/`
- `/shareme:generate path:/abs/path/to/skill` — operates on an arbitrary path
- `/shareme:generate <skill-name> --sanitize` — also replaces author-specific values in the copy with `${PLACEHOLDER}` syntax

## Workflow when invoked

1. Resolve the target skill path
2. Run `scripts/analyze_skill.py <path> --output /tmp/analysis.json` to produce structured analysis
3. Review the analysis with the user, ask for confirmations on ambiguous detections (brand mentions, edge-case paths)
4. Run `scripts/sanitize_skill.py <path> <skill>_shared --analysis /tmp/analysis.json [--sanitize]` FIRST — this creates the sibling folder and copies the skill with `# TODO_ADAPT:` markers. It refuses to run if the folder already exists.
5. Run `scripts/generate_shareme.py --analysis /tmp/analysis.json --template ../../TEMPLATE.md --output <skill>_shared/SHAREME.md` to write the generated SHAREME.md INTO the just-created folder
6. Show the user the output folder structure and the first 30 lines of the generated `SHAREME.md`
7. Remind the user that they MUST review and edit the generated SHAREME before sharing — automation is a starting point, not a finished product

## Operational notes

- Author-specific detection is heuristic. Always confirm with the user before tagging brand names, product names, or domain-specific terms.
- The `--sanitize` flag is destructive within the copy folder (the original is still untouched). Use it only when the goal is a fully depersonalized export.
- The skill reads `../../TEMPLATE.md`, `../../SPEC.md`, `../../CONVENTIONS.md` from the plugin root. These are the source of truth.
- See `references/shareme-workflow.md` for full operational details.

## Output

A new folder `<skill-name>_shared/` next to the target skill, containing:

```
<skill-name>_shared/
├── SHAREME.md                  # Generated, review before sharing
├── SKILL.md                    # Copy (with markers if --sanitize)
├── <other skill files...>      # Copies (with markers if --sanitize)
```

The user reviews, edits, then decides whether to commit, zip, or publish.
