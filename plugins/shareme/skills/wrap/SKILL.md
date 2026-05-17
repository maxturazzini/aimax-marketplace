---
name: wrap
description: Wraps a Claude Code skill into a SHAREME-compliant adoption package. Produces a sibling folder named `<skill-name>_shared/` containing a copy of the skill with `# TODO_ADAPT:` markers and a `SHAREME.md` following the standard at github.com/maxturazzini/shareme. Use this skill whenever the user wants to share, publish, distribute, or document a Claude Code skill they authored. Trigger keywords - "make this skill shareable", "wrap skill for sharing", "prepare skill for sharing", "document skill for adoption", "create companion doc", "/shareme:wrap".
---

# /shareme:wrap

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

- `/shareme:wrap <skill-name>` — operates on `~/.claude/skills/<skill-name>/`
- `/shareme:wrap path:/abs/path/to/skill` — operates on an arbitrary path
- `/shareme:wrap <skill-name> --sanitize` — also replaces author-specific values in the copy with `${PLACEHOLDER}` syntax

## Workflow when invoked

1. Resolve the target skill path
2. Run `scripts/analyze_skill.py <path> --output /tmp/analysis.json` to produce structured analysis
3. **Review the analysis WITH THE USER and ask for confirmations BEFORE sanitizing**:
   - **Skill rename**: if the skill name embeds an author-specific prefix (e.g. `mt-` for "Max Turazzini"), propose a generic rename and ask. The new name will be applied via `--rename-to`.
   - **Proper-noun candidates** (`proper_noun_candidates` in the analysis): each is a capitalized token recurring ≥3 times across files. Typical hits: author's first name, collaborator names, internal product/brand names. For each high-frequency candidate, ask the user what to replace it with (e.g. `Max → Utente`, `Massimiliano → me`) or whether to keep it. Build a list of `--replace KEY=VALUE` flags from the answers.
   - **Author-specific files**: scan the file list for templates/scripts whose name or content suggests they only make sense in the author's workflow (e.g. a template that references a private project, an integration with a personal automation). Propose excluding them via `--exclude <glob>`.
   - **Path detections**: confirm whether to apply `${PLACEHOLDER}` substitution (`--sanitize`).
4. Run `scripts/sanitize_skill.py <path> <skill>_shared --analysis /tmp/analysis.json [--rename-to NEW_NAME] [--replace KEY=VALUE]... [--exclude GLOB]... [--sanitize]` FIRST — this creates the sibling folder and copies the skill with `# TODO_ADAPT:` markers and the requested transformations. It refuses to run if the folder already exists.
5. Run `scripts/generate_shareme.py --analysis /tmp/analysis.json --template ../../TEMPLATE.md --output <skill>_shared/SHAREME.md` to write the generated SHAREME.md INTO the just-created folder
6. Show the user the output folder structure and the first 30 lines of the generated `SHAREME.md`
7. Remind the user that they MUST review and edit the generated SHAREME before sharing — automation is a starting point, not a finished product

## Operational notes

- **Heuristic detection requires user confirmation**: proper-noun candidates and exclusion suggestions are guesses. Never apply `--replace` or `--exclude` without asking. The user knows which "Max" is a person and which "MAX" is the brand.
- **`--rename-to` only changes content**, not the target folder name. The target folder name comes from the second positional argument to `sanitize_skill.py`. Typically pass the same string to both (e.g. `target=/path/to/aimax-foo_shared` and `--rename-to aimax-foo`).
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
