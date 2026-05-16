# Contributor instructions — shareme plugin

This file is read by Claude Code when working inside this plugin folder (e.g., for fixes, enhancements, or PR review). It is NOT the documentation for users installing the plugin — that lives in [README.md](README.md).

> This plugin lives inside the **aimax-skills** marketplace at `plugins/shareme/`. Marketplace-wide conventions live in the repo-root [`CLAUDE.md`](../../CLAUDE.md). All paths in this file are relative to the plugin folder (`plugins/shareme/`), so run validation commands from here, not from the repo root.

## Plugin purpose

`shareme` is two things in one plugin:

1. **A standard** (`SPEC.md`, `TEMPLATE.md`, `CONVENTIONS.md`) that defines what a SHAREME-compliant companion document looks like
2. **A Claude Code plugin** (`skills/generate/`) that produces SHAREME.md drafts for any target skill

When making changes, keep the two layers consistent. If you change the spec, update the dogfood `skills/generate/SHAREME.md` and the synthetic `examples/example-shareme.md` to match.

## Project structure

```
.claude-plugin/plugin.json    Plugin manifest (name, version, repo)
SPEC.md                       Standard formal specification
TEMPLATE.md                   Boilerplate to copy
CONVENTIONS.md                Placeholder syntax, adapt markers, tone
README.md                     User-facing install + usage docs
examples/                     Synthetic SHAREME examples
skills/generate/              The /shareme:generate skill
  SKILL.md                    Trigger description for Claude Code
  SHAREME.md                  Dogfooding (keep in sync with TEMPLATE.md)
  scripts/                    Python implementation (stdlib only)
  references/                 Operational notes for Claude when invoking the skill
```

## Invariants

When changing code, do not break these:

1. **The original skill is never modified.** `sanitize_skill.py` produces a sibling folder. If a change introduces any write to the source path, it is a bug.
2. **Workflow order**: `analyze` → `sanitize` → `generate`. `sanitize` MUST run before `generate` because it creates the destination folder; `generate` writes into it. Both `SKILL.md` and `references/shareme-workflow.md` document this order — keep them in sync.
3. **Stdlib only**: `scripts/` must run on Python 3.11+ standard library. No third-party deps. `requirements.txt` is reserved for future needs but currently empty.
4. **Spec coherence**: any new required section in `SPEC.md` must also appear in `TEMPLATE.md`, in `examples/example-shareme.md`, and in `skills/generate/SHAREME.md`.

## Validate after changes

Before committing, dogfood the skill on itself:

```bash
python3 skills/generate/scripts/analyze_skill.py skills/generate --output /tmp/self.json
rm -rf /tmp/generate_shared
python3 skills/generate/scripts/sanitize_skill.py skills/generate /tmp/generate_shared --analysis /tmp/self.json --sanitize
python3 skills/generate/scripts/generate_shareme.py --analysis /tmp/self.json --template TEMPLATE.md --output /tmp/generate_shared/SHAREME.md
diff /tmp/generate_shared/SHAREME.md skills/generate/SHAREME.md  # expect prose-heavy sections to differ; structure should match
```

If the structure of the generated file no longer matches the dogfood, either the template or the dogfood drifted — fix the inconsistency before committing.

## Commit identity

This repo uses identity `maxturazzini / max@turazzini.com` for commits. Verify with `git config user.name` before committing if in doubt. Do not change global git config — set it locally for this repo.

## Out of scope (for now)

- Windows path detection (only macOS / Linux paths are detected today)
- Secret scanning (use a dedicated tool — `gitleaks`, `trufflehog`)
- LLM-assisted prose generation (sections 2, 6, 7 of the SHAREME are intentionally left as `<TODO: ...>` for human input)
- Multi-skill batch processing
