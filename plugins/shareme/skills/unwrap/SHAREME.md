# SHAREME — `unwrap`

> Companion document to `SKILL.md`. Read this **before** installing or running the skill.
>
> *This skill is part of the SHAREME plugin and is the adoption counterpart of `/shareme:wrap`. Together they form the full lifecycle: wrap to share, unwrap to adopt.*

## 1. What this is

A Claude Code skill that adopts an external Claude Code skill consciously. It resolves the source (path, GitHub URL, zip, or installed-skill name), runs a decoupled security review, reads or infers a `SHAREME.md`, walks `# TODO_ADAPT:` markers interactively, and installs the skill at the right destination.

## 2. What I can do

- **Resolve any skill source** — local folder, GitHub URL (shallow clone), zip file, or installed-skill name.
  Example: `/shareme:unwrap https://github.com/someone/their-skill`
- **Run a decoupled security review** — spawn `claude -p` or `codex exec` in a subprocess with a hardened anti-injection system prompt, return a structured verdict.
  Example: same invocation as above; the review runs unconditionally.
- **Read or infer a SHAREME companion** — read existing `SHAREME.md` and cross-check against analyzer facts; if absent, write a `SHAREME.inferred.md` next to `SKILL.md` with explicit disclaimer.
  Example: `/shareme:unwrap /path/to/skill-without-shareme` produces `/path/to/skill-without-shareme/SHAREME.inferred.md`
- **Walk `# TODO_ADAPT:` markers interactively** — group by category, batch-prompt for replacement values, apply substitutions in dry-run first.
  Example: `/shareme:unwrap weather-bot` (an installed skill) walks every marker and updates the folder in place after confirmation.
- **Install at the right destination** — auto-detect skill vs. plugin, choose `~/.claude/skills/` or repo-scoped `.claude/skills/` (only if pwd is a git repo), or guide the user to `claude plugin install` when the source is a plugin.
  Example: dry-run by default, `--apply` commits.

## 3. What I do NOT do

- **No execution of the skill's code** during review. The security review is static analysis in a decoupled subprocess. The skill's own scripts are never invoked by unwrap.
- **No secret scanning.** The reviewer flags suspicious patterns but is not a credentials scanner. Run `gitleaks` or `trufflehog` separately if the source might contain leaked tokens.
- **No fix of broken skills.** If the source has bugs, unwrap documents them via the security review and stops. It does not patch logic errors.
- **No automatic uninstall of conflicting versions.** If the target install destination already exists, unwrap asks. It never overwrites silently.
- **No copy of plugin files.** When the source is a plugin (has `.claude-plugin/plugin.json`), unwrap audits and reports but routes the user to `claude plugin install` for the actual installation. Plugins have a lifecycle; unwrap doesn't bypass it.
- **No internet access beyond the source URL.** Unwrap clones the github URL or downloads the zip the user pointed at. It does not call out to other services during review or adaptation.

## 4. What I do behind the scenes

- **Network calls**:
  - `gh repo view` / `git clone --depth 1` only if the input is a GitHub URL — to fetch the source and provenance (owner, stars, last commit).
  - `curl` / `wget` only if the input is a remote zip URL — to download the archive.
  - **None otherwise**. The security review subprocess runs locally; no telemetry, no external lookups.
- **File system writes**:
  - Source folder: writes `SHAREME.inferred.md` only when SHAREME.md is missing.
  - Install destination (`~/.claude/skills/<name>/`, `./.claude/skills/<name>/`, or `~/.claude/skills/<name>.bak/` for backups): writes adapted files only after explicit `--apply` confirmation.
  - `/tmp/`: shallow clones, zip extracts, analyzer JSON, subprocess prompt/response logs.
  - Never writes outside these three roots.
- **External services**: none persistent. GitHub API only via `gh` CLI (read-only) when the input is a URL.
- **Persistent state**: none. Each invocation is independent. The reused `analyze_skill.py` output goes to `/tmp/` and is not cached across runs.
- **Tools used**: Python 3.11+ standard library, `git` or `gh` (only for URL inputs), `unzip` (only for zip inputs), and one of `claude` / `codex` CLI for the decoupled security review (with fallback to internal Agent).

## 5. What is author-specific

| What | Where | Why | How to change |
|---|---|---|---|
| Install destination defaults | resolution logic in `references/unwrap-workflow.md` §7 | Claude Code convention: skills live in `~/.claude/skills/` for user-scope, `./.claude/skills/` for repo-scope | If your team uses a different layout, adjust the decision tree or always pass `path:/abs/dest/` |
| Backup suffix `.bak/` | `references/unwrap-workflow.md` §8 | Standard suffix, no naming collision with skill folders | Change to `.backup/`, `.orig/`, or a timestamped variant if you have a team convention |
| Security review CLI fallback order (claude → codex → Agent) | `references/unwrap-workflow.md` §4 | Both CLIs are commonly available among adopters; Agent fallback keeps the skill functional without external CLI | Swap the order if your environment prefers Codex, or hard-fail if you only trust one backend |

Unwrap is intentionally generic. The list above is short because the design absorbs author-specific bits into convention rather than configuration.

## 6. What you might do with it

- **First-time adoption** — install a skill you just found on GitHub, with full security audit and guided adaptation
- **Bulk audit of installed skills** — run unwrap in dry-run on every folder in `~/.claude/skills/` to surface what each one actually does
- **Pre-install review** — point unwrap at a source URL without `--apply` to get the security verdict + inferred SHAREME before deciding whether to install
- **Migration audit** — before moving skills between machines, run unwrap on each to catch host-specific paths and tokens
- **Teaching tool** — show new team members what conscious skill adoption looks like, by running unwrap on a real third-party skill end-to-end

## 7. Onboarding questions

Answer these before using the skill:

1. Do you have either `claude` CLI or `codex` CLI installed? (Without one of these, the security review falls back to an internal Agent and loses context decoupling — usable but weaker.)
2. Is the source you want to adopt a single skill folder, a plugin with `.claude-plugin/plugin.json`, or a marketplace repo containing multiple plugins? (Unwrap routes each case differently — only the first one results in a file copy.)
3. Do you intend to use the skill across all your projects, or only inside one repo? (Determines `~/.claude/skills/` vs. `./.claude/skills/`. Repo-scope only offered when pwd is a git repo.)
4. Are you adopting from a known author (GitHub repo with history) or an anonymous source (zip from a forum / pastebin)? (Anonymous sources trigger a stricter security review.)
5. If the source has no `SHAREME.md`, are you willing to accept an inferred one written by unwrap, or do you want to stop and ask the author to write a proper one?

## 8. Technical prerequisites

- **Runtime**: Python 3.11 or newer (matches the `wrap` skill — both share `analyze_skill.py`)
- **OS**: macOS or Linux. Windows path detection inherits `wrap`'s gaps.
- **Dependencies**: Python standard library only for unwrap's own scripts. External: `git` or `gh` for GitHub URLs, `unzip` for zip inputs.
- **OS permissions**: read access to the source, write access to the install destination, write access to `/tmp/` for the subprocess and clone working area.
- **Accounts and tokens**: none required by unwrap itself. `gh` CLI may require GitHub auth for private repos. The security review subprocess may require Claude or OpenAI API access depending on which CLI is used.

## 9. Cyber and security warnings

- **The security review is heuristic, not a guarantee.** A determined attacker can still hide malicious behavior — obfuscated code, dynamic eval, network calls disguised as data processing. Treat the verdict as "this is what static analysis can see", not "this skill is safe".
- **Decoupling reduces but does not eliminate prompt-injection risk.** The subprocess runs with a hardened system prompt instructing the reviewer to not execute or follow instructions from the analyzed code. This is best-effort. If the source aggressively tries to manipulate the reviewer (rare but possible), the verdict can be unreliable.
- **`--force` is a footgun.** It exists for cases where the user understands the red findings and accepts the risk (e.g., they wrote the code themselves and recognize a false positive). It is not a "skip safety" toggle. The skill insists with a final CONFIRM prompt to reduce accidental use.
- **In-place adaptation without backup or git is irreversible.** If you run unwrap on an installed skill with `--no-backup` and the folder is not a git repo, you have no undo. The skill refuses to proceed without one of: a backup, a git repo, or an explicit `--no-backup` flag.
- **Anonymous zip sources should be treated as hostile by default.** A zip from a forum, pastebin, or unknown URL has no accountability. Unwrap flags this in the provenance step and biases the review stricter, but the adopter's judgment matters most. Don't unzip-and-install random files.
- **MCP servers and hooks are surface for escalation.** If the skill registers an MCP server (in `.claude/settings.json` or `~/.claude/settings.json`) or adds hooks, those changes affect every future Claude Code session, not just this skill's invocation. Unwrap surfaces these explicitly before install — read the section, don't skim.
- **The subprocess CLI may send the analyzed code to a remote LLM.** `claude -p` and `codex exec` upload prompt + context to Anthropic / OpenAI APIs respectively. If the source contains sensitive data (rare but possible), this is a data egress event. Use the Agent fallback for fully local review.

## 10. How to adapt

For most users, no adaptation is needed — unwrap runs as-is. If you need to extend it:

1. **Change install destination defaults**: edit the decision tree in `references/unwrap-workflow.md` §7
2. **Change backup naming**: edit `BACKUP_SUFFIX` in `scripts/install.py` (added in the scripts phase)
3. **Reorder security review fallback**: edit the fallback chain in `scripts/security_review.py` (added in the scripts phase)
4. **Add Windows support**: extend `analyze_skill.py` `PATH_PATTERNS` (inherited from the `wrap` skill — change once, both benefit)
5. **Customize the inferred SHAREME template**: edit `references/inferred-template.md` (added in the scripts phase) — kept smaller than the full 11-section spec on purpose

Verify with: `/shareme:unwrap <path-to-some-skill>` (dry-run is the default) and inspect the proposed diff before applying with `--apply`.

## 11. License and disclaimer

- **License**: MIT (see [`LICENSE`](../../LICENSE))
- **Warranty**: none. The security review is a tool, not a substitute for human judgment. The adopter decides.
- **Attribution**: not required, appreciated. Link back to `github.com/maxturazzini/aimax-skills`.
- **Contact**: open an issue at `github.com/maxturazzini/aimax-skills/issues`.

---

## Optional sections

### Provenance

Written as the adoption counterpart of `/shareme:wrap`. Together they implement the SHAREME contract end-to-end: wrap makes a skill shareable with full disclosure, unwrap makes adoption conscious with full audit. Neither side can be replaced by docs alone — wrap automates the "this is what my skill does" part, unwrap automates the "this is what I'm about to install" part.

### Alternatives

- **Manual adoption** — read SHAREME.md, grep for TODO_ADAPT, edit by hand, copy folder. Works for small skills you trust. Unwrap is for everything else.
- **`git clone` + `claude plugin install`** — works for plugins from known authors when you don't need the audit step. Unwrap is for sources where the audit is the point.

### Roadmap

Possible future direction (no commitments):
- Codex CLI adapter implementation (currently a design contract)
- Batch mode: `/shareme:unwrap --all ~/.claude/skills/` to audit every installed skill in one pass
- Cached security verdicts (with explicit cache-bust on source change) to avoid re-reviewing unchanged skills
- Windows path handling parity with `wrap`

### Changelog

- v0.1.0 — initial release (docs only; scripts follow)
