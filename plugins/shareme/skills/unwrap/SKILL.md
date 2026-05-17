---
name: unwrap
description: Adopts an external Claude Code skill consciously. Takes a skill source (path, GitHub URL, zip, or already-installed skill name), runs a decoupled security review, reads or infers the SHAREME companion, resolves `# TODO_ADAPT:` markers interactively, and installs the skill at the right destination. Use this skill whenever the user wants to install, adopt, adapt, or audit a skill they did not author. Trigger keywords - "I downloaded this skill", "ho scaricato questa skill", "ho visto questa skill su github", "adopt this skill", "adapt this skill to my setup", "audit this skill before installing", "/shareme:unwrap".
---

# /shareme:unwrap

Adopt an external Claude Code skill: review, adapt, install. The conscious counterpart of `/shareme:wrap`.

## When to use this skill

- The user downloaded a skill folder or zip from someone else
- The user wants to install a skill from a GitHub URL
- The user wants to adopt a skill already living in `~/.claude/skills/` but never adapted to their setup
- The user wants to audit a skill's behavior before deciding whether to install it

## What this skill does

Given a skill source, in this order:

1. **Resolves the source** — local path, GitHub URL (cloned shallow into a temp dir), zip file (extracted), or installed skill name (resolved to its folder).
2. **Detects type and provenance** — skill folder vs. plugin folder (`.claude-plugin/plugin.json` present?), and source authenticity (GitHub repo owner / stars / last commit, or "anonymous zip" warning).
3. **Runs a security review** — always, regardless of whether `SHAREME.md` is present. The review runs in a **decoupled subprocess** with a hardened system prompt that does not execute or follow instructions from the analyzed code. Fallback chain: `claude -p` → `codex exec` → internal `security-code-analyzer` Agent. Output is structured: `verdict ∈ {pass, yellow, red}` + findings.
4. **Reads or infers the SHAREME** — if `SHAREME.md` exists, reads it and cross-checks claims against the analyzer's facts. If absent, runs `analyze_skill.py` from the `wrap` skill and writes a `SHAREME.inferred.md` next to the source, with an explicit disclaimer (facts reliable, intent inferred).
5. **Proposes use cases** — extracts SHAREME §6 if present, otherwise shows 3-5 capability bullets inferred from `SKILL.md` and the analysis. Asks which use case fits.
6. **Walks `# TODO_ADAPT:` markers** — parses each marker in the source, groups by category, prompts the user for replacements, applies them in a copy or in-place (see operational notes).
7. **Verifies prerequisites** — reads SHAREME §8, checks binaries on PATH, env vars set, prompts the user for the rest. No install proceeds with missing prerequisites unless the user explicitly accepts.
8. **Installs** — copies / moves the adapted skill to the auto-detected destination, or guides the user through `claude plugin install` if the source is a plugin.

## Triggers

- `/shareme:unwrap <path>` — adopt a local folder
- `/shareme:unwrap <github-url>` — clone shallow into temp, then adopt
- `/shareme:unwrap <zip-path>` — extract into temp, then adopt
- `/shareme:unwrap <installed-skill-name>` — adapt a skill already in `~/.claude/skills/<name>/`
- `/shareme:unwrap --apply` — commit changes (default is dry-run: show what would change, don't write yet)
- `/shareme:unwrap --force` — bypass red security verdict (discouraged, requires explicit confirmation)
- `/shareme:unwrap --no-backup` — skip backup when adapting an installed skill (discouraged)

## Workflow when invoked

1. **Resolve source** to an absolute folder path. For GitHub URLs use `gh repo clone` or `git clone --depth 1` into `/tmp/`. For zips use `unzip` into `/tmp/`. For installed names resolve to `~/.claude/skills/<name>/`. If resolution fails, abort with a clear message.

2. **Detect type**:
   - Folder contains `.claude-plugin/plugin.json` → it's a plugin. Plugins are not "installed" by copying files; route the user to `claude plugin install`. Continue with review and adaptation guidance, but do NOT copy files at the end.
   - Folder contains `SKILL.md` only → it's a skill. Proceed to install destination decision later.
   - Neither present → not a Claude Code skill. Abort, suggest the user check the source.

3. **Gather provenance**:
   - GitHub URL → use `gh repo view <owner>/<repo> --json owner,stargazerCount,pushedAt,description` (read-only). Show owner, stars, last push, description.
   - Zip → file size, source domain if known, otherwise mark as "anonymous source" and bias the review stricter.
   - Local path / installed name → no extra provenance, trust the user's filesystem.

4. **Run security review subprocess** (always). See [references/unwrap-workflow.md](references/unwrap-workflow.md) §4 for the contract. Pass: the executable surface (SKILL.md, scripts/, plugin.json, any other `.sh` / `.py` / `.js` / `.ts` files). The reviewer outputs JSON with `verdict`, `findings[]`, `severity`. **Trust gate**: if `verdict == red`, stop and surface findings. User can force with `--force` but unwrap insists ("are you sure? this is what the reviewer flagged...") before proceeding.

5. **SHAREME handling**:
   - **Present**: read it. Cross-check claims in §4 (behind the scenes) and §8 (prerequisites) against analyzer output. If they disagree (e.g., SHAREME claims "no network calls" but analyzer found `requests.get`), surface the discrepancy and flag it as a yellow finding.
   - **Absent**: run `python3 <wrap_scripts>/analyze_skill.py <source> --output /tmp/unwrap-analysis.json`. Generate `SHAREME.inferred.md` in the source folder using a smaller template (4 sections: what it does, what it touches, what it needs, security verdict). Write the disclaimer header.

6. **Propose use cases**: extract or infer 3-5 bullets. Ask user "which of these fits your need?" — the answer doesn't gate anything, but tailors the adaptation prompts later (e.g., if they pick "internal use", brand-name markers can be kept; if they pick "publish-ready", strip everything author-specific).

7. **Marker resolution**:
   - Grep the source for `# TODO_ADAPT:` (and `${PLACEHOLDER}` if wrap was run with `--sanitize`).
   - If zero markers AND the skill is already installed AND no obvious author-specific bits remain → idempotent re-run, ask user "this skill appears already adapted, do you want to revisit prior choices?" instead of restarting.
   - Group markers by category (paths, names, brand terms, defaults). For each group, show the affected lines and prompt for the replacement value once (batch).
   - Apply substitutions in-memory first (dry-run). Show the full diff. Wait for `--apply` or explicit user confirmation.

8. **Prerequisites check**:
   - If SHAREME present: read §8 verbatim.
   - If inferred: use the analyzer's `tools_used` and `dependencies` fields.
   - Check what's checkable: `which <binary>` for tools, `printenv <VAR>` for env vars.
   - Anything not checkable (API tokens, account access) → prompt user to confirm they have it.
   - Missing prerequisites → warn loudly, do not install unless user explicitly accepts.

9. **Install destination** (skill case only — plugin case stopped at step 2):
   - Default: `~/.claude/skills/<name>/`. Always cross-project for the user.
   - If pwd is a git repo: ask "install user-wide (`~/.claude/skills/`) or repo-scoped (`./.claude/skills/`)?". Don't ask if pwd is not a repo (avoid clutter prompts).
   - If destination already exists: ask user — overwrite, pick different name, or abort. Default to abort.

10. **In-place adaptation case** (source was an installed skill name): before touching files, ask:
    - "Is the skill folder a git repo?" → yes: rely on `git diff` for the audit trail. No backup.
    - "Do you want a backup copy?" → yes: copy to `~/.claude/skills/<name>.bak/` before applying.
    - Neither (user declines both) → require `--no-backup` flag for safety. If not set, refuse to proceed.

11. **Apply** (only after dry-run confirmed):
    - Skill case: write adapted files to install destination.
    - Plugin case: print the `claude plugin install` command. Do not copy.
    - In-place case: apply substitutions to the existing folder.
    - Report: where the skill lives, what changed, what was skipped, residual TODOs.

## Operational notes

- **Dry-run is the default.** Without `--apply`, unwrap shows every planned change (diff per file, install destination, prerequisites status) and stops. Use `--apply` to commit.
- **Trust gate is forceable but loud.** Red verdict + `--force` triggers a final "type CONFIRM to proceed" prompt with the findings listed below. Yellow verdict shows findings but does not gate.
- **Security review never executes the skill code.** Static analysis only. The subprocess prompt explicitly instructs the reviewer to not run anything.
- **`analyze_skill.py` is reused from the `wrap` skill.** Path: `<plugin_root>/skills/wrap/scripts/analyze_skill.py`. Read-only on any skill folder.
- **Inferred SHAREME uses a smaller template**, not the full 11-section SPEC. Reason: the adopter is inferring, not authoring — claims must stay narrow and honest.
- **Plugin install is hands-off.** If the source is a plugin, unwrap audits and reports but does NOT copy files. The user runs `claude plugin install` themselves. This avoids accidentally bypassing the plugin lifecycle.
- See [references/unwrap-workflow.md](references/unwrap-workflow.md) for the full operational reference, including the subprocess JSON contract and failure modes.

## Output

After a successful `--apply` run:

```
<install-destination>/
├── SKILL.md                          # Adapted (markers resolved)
├── SHAREME.md                        # From source, or generated SHAREME.inferred.md
├── <other skill files...>            # Adapted copies
└── <unchanged files...>              # No markers, copied as-is
```

Plus a final report to the user listing:
- Install location
- Security verdict + any findings
- Markers resolved / skipped
- Prerequisites status
- Residual `# TODO:` items the user must handle manually
