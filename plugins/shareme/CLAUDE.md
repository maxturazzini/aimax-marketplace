# Contributor instructions — shareme plugin

This file is read by Claude Code when working inside this plugin folder (e.g., for fixes, enhancements, or PR review). It is NOT the documentation for users installing the plugin — that lives in [README.md](README.md).

> This plugin lives inside the **aimax-marketplace** marketplace at `plugins/shareme/`. Marketplace-wide conventions live in the repo-root [`CLAUDE.md`](../../CLAUDE.md). All paths in this file are relative to the plugin folder (`plugins/shareme/`), so run validation commands from here, not from the repo root.

## Plugin purpose

`shareme` is two things in one plugin:

1. **A standard** (`SPEC.md`, `TEMPLATE.md`, `CONVENTIONS.md`) that defines what a SHAREME-compliant companion document looks like
2. **A Claude Code plugin with two skills** — the two sides of the SHAREME contract:
   - `skills/wrap/` — the **author side**: produces SHAREME.md drafts and `# TODO_ADAPT:` markers for any skill you authored
   - `skills/unwrap/` — the **adopter side**: takes an external skill (path / URL / zip / installed name), runs a decoupled security review, reads or infers SHAREME, walks markers interactively, installs at the right destination

When making changes, keep all three layers consistent. If you change the spec, update the dogfood `skills/wrap/SHAREME.md`, the dogfood `skills/unwrap/SHAREME.md`, and the synthetic `examples/example-shareme.md` to match.

## Project structure

```
.claude-plugin/plugin.json    Plugin manifest (name, version, repo)
SPEC.md                       Standard formal specification
TEMPLATE.md                   Boilerplate to copy
CONVENTIONS.md                Placeholder syntax, adapt markers, tone
README.md                     User-facing install + usage docs
examples/                     Synthetic SHAREME examples
skills/wrap/                  The /shareme:wrap skill (author side)
  SKILL.md                    Trigger description for Claude Code
  SHAREME.md                  Dogfooding (keep in sync with TEMPLATE.md)
  scripts/                    Python implementation (stdlib only)
  references/                 Operational notes for Claude when invoking the skill
skills/unwrap/                The /shareme:unwrap skill (adopter side)
  SKILL.md                    Trigger description for Claude Code
  SHAREME.md                  Dogfooding (keep in sync with TEMPLATE.md)
  references/                 Operational notes for Claude when invoking the skill
                              (scripts/ to follow in a later phase)
```

## Invariants

When changing code, do not break these:

1. **The original skill is never modified.** `sanitize_skill.py` produces a sibling folder. If a change introduces any write to the source path, it is a bug.
2. **Workflow order**: `analyze` → `sanitize` → `generate`. `sanitize` MUST run before `generate` because it creates the destination folder; `generate` writes into it. Both `SKILL.md` and `references/shareme-workflow.md` document this order — keep them in sync.
3. **Stdlib only**: `scripts/` must run on Python 3.11+ standard library. No third-party deps. `requirements.txt` is reserved for future needs but currently empty.
4. **Spec coherence**: any new required section in `SPEC.md` must also appear in `TEMPLATE.md`, in `examples/example-shareme.md`, in `skills/wrap/SHAREME.md`, and in `skills/unwrap/SHAREME.md`.
5. **Unwrap is doc-only at this stage.** `skills/unwrap/scripts/` does not exist yet — the design contract for scripts lives in `skills/unwrap/references/unwrap-workflow.md`. Do not commit half-implemented scripts; either implement the full subprocess + marker resolution loop or keep it at doc-level.

## Validate after changes

Before committing, dogfood the wrap skill on itself:

```bash
python3 skills/wrap/scripts/analyze_skill.py skills/wrap --output /tmp/self.json
rm -rf /tmp/wrap_shared
python3 skills/wrap/scripts/sanitize_skill.py skills/wrap /tmp/wrap_shared --analysis /tmp/self.json --sanitize
python3 skills/wrap/scripts/generate_shareme.py --analysis /tmp/self.json --template TEMPLATE.md --output /tmp/wrap_shared/SHAREME.md
diff /tmp/wrap_shared/SHAREME.md skills/wrap/SHAREME.md  # expect prose-heavy sections to differ; structure should match
```

If the structure of the generated file no longer matches the dogfood, either the template or the dogfood drifted — fix the inconsistency before committing.

Then sanity-check `unwrap` (docs-only at this stage):

```bash
python3 skills/wrap/scripts/analyze_skill.py skills/unwrap --output /tmp/unwrap-self.json
# Confirms the analyzer (which unwrap will reuse) doesn't choke on the unwrap skill folder.
# Inspect /tmp/unwrap-self.json: detected paths, network patterns, etc. should be empty or minimal,
# since unwrap has no scripts yet.
```

## Commit identity

This repo uses identity `maxturazzini / max@turazzini.com` for commits. Verify with `git config user.name` before committing if in doubt. Do not change global git config — set it locally for this repo.

## Out of scope (for now)

- Windows path detection (only macOS / Linux paths are detected today)
- Secret scanning (use a dedicated tool — `gitleaks`, `trufflehog`)
- LLM-assisted prose generation (sections 2, 6, 7 of the SHAREME are intentionally left as `<TODO: ...>` for human input)
- Multi-skill batch processing
