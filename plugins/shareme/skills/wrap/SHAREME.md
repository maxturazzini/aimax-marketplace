# SHAREME — `wrap`

> Companion document to `SKILL.md`. Read this **before** installing or running the skill.
>
> *This skill is part of the SHAREME plugin and is its own first example. If this file looks weird, it means we broke our own standard.*

## 1. What this is

A Claude Code skill that produces a SHAREME-compliant adoption package for any other Claude Code skill. Output is a sibling folder named `<target-skill>_shared/` containing a copy with `# TODO_ADAPT:` markers and a generated `SHAREME.md`.

## 2. What I can do

- **Analyze a target skill** — detect hardcoded paths, network calls, file system writes, MCP servers, external tools, Python dependencies.
  Example: `python scripts/analyze_skill.py ~/.claude/skills/weather-bot --json`
- **Generate a SHAREME.md draft** — fill the standard template with detected facts.
  Example: `python scripts/generate_shareme.py --analysis /tmp/x.json --template ../../TEMPLATE.md --output /tmp/SHAREME.md`
- **Produce a sibling `_shared/` copy** — copy the skill folder, insert `# TODO_ADAPT:` markers above detected lines.
  Example: `python scripts/sanitize_skill.py ~/.claude/skills/weather-bot ./weather-bot_shared --analysis /tmp/x.json`
- **Optionally apply placeholders** — replace detected author-specific paths with `${PLACEHOLDER}` syntax (only in the copy).
  Example: same as above, with `--sanitize` flag

## 3. What I do NOT do

- **No semantic understanding** — the skill is regex-based. It detects *patterns* (path-like strings, function calls, URLs), not *meaning*. Brand names, domain-specific jargon, and ambiguous proper nouns are flagged for the user to confirm, not auto-classified.
- **No automatic publishing** — the skill produces a folder. It does not git commit, zip, push, email, or upload anything.
- **No multi-language support** — the generated `SHAREME.md` is in English. Translation is the adopter's job.
- **No skill repair** — if the target skill is broken, this skill won't fix it. It documents what is, not what should be.
- **No deletion** — the original target skill is never modified. The output is always a new sibling folder.

## 4. What I do behind the scenes

- **Network calls**: none. The skill operates entirely on local files.
- **File system writes**: creates a sibling folder `<target-skill>_shared/` next to the target skill. With `--sanitize`, also modifies files inside that copy. Never writes outside the target's parent directory.
- **External services**: none.
- **Persistent state**: none. Each invocation is independent.
- **Tools used**: Python 3.11+ standard library only (no third-party deps).
- **Reads**: every text file inside the target skill folder, plus `TEMPLATE.md`, `SPEC.md`, `CONVENTIONS.md` from the plugin root.

## 5. What is author-specific

| What | Where | Why | How to change |
|---|---|---|---|
| Default `~/.claude/skills/` lookup path | resolution logic in `references/shareme-workflow.md` | Claude Code installs skills there by convention | If a user installs Claude Code skills elsewhere, pass `path:/abs/...` instead of a name |
| Comment markers per file extension | `scripts/sanitize_skill.py:14-23` | Covers common languages (Python, Shell, YAML, JS/TS, Markdown, HTML, CSS) | Add an entry to `COMMENT_BY_EXT` for languages not covered |
| Path detection regex (Users/, home/, OneDrive, iCloud, Dropbox) | `scripts/analyze_skill.py:18-25` | Covers macOS, Linux, common cloud storage | Extend `PATH_PATTERNS` for Windows paths, other cloud providers, or organization-specific layouts |

The skill itself is intentionally generic. The list above is short on purpose.

## 6. What you might do with it

- **Pre-publish audit** — run on a skill before opening a PR, see what regex detects, fix what shouldn't ship
- **Inherited skill review** — when joining a team, run on every existing skill to map "what does this thing actually touch"
- **Compliance documentation** — generate SHAREME.md for an internal skill registry where every skill must declare its side effects
- **Teaching tool** — show new contributors what a "proper" skill SHAREME.md looks like, by running it on their first skill
- **Migration prep** — generate `_shared/` copies of all your skills before changing your username, moving folders, switching cloud providers

## 7. Onboarding questions

Answer these before using the skill:

1. Do you author your own Claude Code skills, or do you mainly install others'? (This skill helps the former.)
2. Is your goal to share publicly, share with a small group, or just self-document? (The `--sanitize` flag matters more for public sharing.)
3. Are your skills already organized under `~/.claude/skills/`, or somewhere else? (Determines whether to use the name shortcut or always pass a path.)
4. Do you trust regex-based detection enough to use it as a first pass, or do you want to manually audit every line? (The output is always a draft — never blindly publish.)

## 8. Technical prerequisites

- **Runtime**: Python 3.11 or newer (uses `from __future__ import annotations` and modern type hints)
- **OS**: any (macOS / Linux / Windows). Path detection is biased toward macOS and Linux; Windows path patterns may need extending.
- **Dependencies**: Python standard library only. `requirements.txt` is reserved for future deps.
- **OS permissions**: read access to the target skill folder, write access to its parent (to create the sibling `_shared/` folder).
- **Accounts and tokens**: none.

## 9. Cyber and security warnings

- **Detection is heuristic, not security-grade**. Do not treat this skill as a secret scanner. It does not detect API keys, tokens, or credentials embedded in code. Run a dedicated secret scanner (`gitleaks`, `trufflehog`, etc.) before publishing.
- **The generated `SHAREME.md` is a draft**. Section 9 of the output ("Cyber and security warnings") will only contain the structural placeholder unless you fill it in. Do not ship without a human review.
- **`--sanitize` modifies file contents in the copy**. If you committed the `_shared/` folder before sanitization completed, you may have committed half-replaced files. Always run sanitize before adding to git.
- **Path detection may produce false negatives**. A path that doesn't match the regex won't be flagged. Read the `_shared/` copy yourself before sharing.

## 10. How to adapt

For most users, no adaptation is needed — the skill runs as-is.

If you need to extend it:

1. **Add path patterns** for environments not covered (Windows, organization-specific paths): edit `PATH_PATTERNS` in `scripts/analyze_skill.py`
2. **Add comment styles** for languages not covered: edit `COMMENT_BY_EXT` in `scripts/sanitize_skill.py`
3. **Customize placeholder names**: edit `PLACEHOLDER_BY_KIND` in `scripts/sanitize_skill.py`
4. **Tune external tool detection**: edit `EXTERNAL_TOOL_HINTS` in `scripts/analyze_skill.py`
5. **Change the template**: edit `<plugin_root>/TEMPLATE.md` — the skill reads it at every invocation, so changes apply immediately

Verify with: `python scripts/analyze_skill.py /path/to/some/skill` and check the JSON output.

## 11. License and disclaimer

- **License**: MIT (see [`LICENSE`](../../LICENSE))
- **Warranty**: none. The skill produces drafts; the human reviews and ships.
- **Attribution**: not required, appreciated. Link back to `github.com/maxturazzini/shareme`.
- **Contact**: open an issue at `github.com/maxturazzini/shareme/issues`.

---

## Optional sections

### Provenance

Written as the bootstrap example for the SHAREME standard. The skill describes itself with the same standard it generates for others — if it ever stops being SHAREME-compliant, the standard has drifted from the implementation, and one of them is wrong.

### Roadmap

Possible future direction:
- Optional LLM pass for prose generation in sections 2, 6, 7
- Detection of Windows paths
- Plugin-level skills that operate on multiple skills at once (batch SHAREME generation)
- A `validate` companion skill that checks an existing SHAREME.md against the spec

No commitments.
