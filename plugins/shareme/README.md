# SHAREME

**A standard for sharing Claude Code skills consciously.**

![version](https://img.shields.io/badge/version-0.1.0-blue) ![status](https://img.shields.io/badge/status-initial%20release-brightgreen) ![license](https://img.shields.io/badge/license-MIT-lightgrey)

> **v0.1.0 — Initial release.** First public, tagged version of SHAREME. Ships the full standard (`SPEC.md`, `TEMPLATE.md`, `CONVENTIONS.md`), a working example, and the two-sided Claude Code plugin: `/shareme:wrap` (author side, fully functional) and `/shareme:unwrap` (adopter side, design + docs released; scripts follow). The standard is intentionally small at this stage and will evolve toward v1.0 based on real-world adoption — any breaking change will be called out in the release notes.

Installing a skill from someone else's environment without reading what it does is reckless. Even when a skill has no obvious customizations, it still does things. It writes files, makes network calls, depends on tools, assumes runtimes. The adopter has the right and the duty to know **what** before deciding **whether**.

`SHAREME.md` is a companion file that lives next to a skill's `SKILL.md` and answers, in five minutes of reading, the questions that should never be skipped.

> Skills are adopted, not magically installed. Unless you enjoy risking your context window.

## What you get

This repository contains:

1. **The standard** — [`SPEC.md`](SPEC.md) defines the eleven sections every SHAREME.md must include.
2. **A boilerplate** — [`TEMPLATE.md`](TEMPLATE.md) you can copy and fill in for your own skill.
3. **Conventions** — [`CONVENTIONS.md`](CONVENTIONS.md) for placeholders, adapt markers, naming, tone.
4. **A working example** — [`examples/example-shareme.md`](examples/example-shareme.md).
5. **Two Claude Code skills** — the two sides of the SHAREME contract:
   - `/shareme:wrap` — for the **author**: turn a skill you wrote into a SHAREME-compliant package ready to share.
   - `/shareme:unwrap` — for the **adopter**: take a skill someone else wrote, run a security review, resolve adaptation markers interactively, install at the right destination.

## Install

`shareme` lives inside the **aimax-marketplace** marketplace. You register the marketplace once, then install any plugin from it on demand:

```bash
# 1. Register the marketplace (once)
claude plugin marketplace add maxturazzini/aimax-marketplace

# 2. Install the shareme plugin from it
claude plugin install shareme@aimax-marketplace
```

The first command clones the marketplace repo into `~/.claude/plugins/marketplaces/aimax-marketplace/`. The second installs `shareme`. Both skills — `/shareme:wrap` and `/shareme:unwrap` — become available in any Claude Code session.

### Verify

```bash
claude plugin list
```

You should see `shareme` in the output. In a Claude Code session, typing `/shareme:` should suggest both `wrap` and `unwrap` as available.

### Update later

```bash
claude plugin marketplace update aimax-marketplace   # pulls latest changes (also shows newly added plugins)
claude plugin update shareme                     # applies updates to shareme (restart required)
```

### Uninstall

```bash
claude plugin uninstall shareme
# (leave the marketplace registered if you have other aimax-marketplace plugins installed)
claude plugin marketplace remove aimax-marketplace
```

### Try it without installing (development / one-shot)

To test a local clone or a fork without going through the marketplace:

```bash
git clone https://github.com/maxturazzini/aimax-marketplace.git
claude --plugin-dir ./aimax-marketplace/plugins/shareme
```

The plugin is loaded for that single Claude Code session only.

## Use as author — `/shareme:wrap`

In a Claude Code conversation, ask in plain language:

> "Wrap my `weather-bot` skill for sharing — generate a SHAREME for it."

Or invoke the skill directly:

```
/shareme:wrap weather-bot
```

Or pass an absolute path if your skills don't live in `~/.claude/skills/`:

```
/shareme:wrap path:/Users/me/projects/my-skill
```

Add `--sanitize` to also replace detected author-specific values with `${PLACEHOLDER}` syntax in the copy:

```
/shareme:wrap weather-bot --sanitize
```

### What happens

The skill creates a sibling folder `weather-bot_shared/` next to the original, containing:
- A copy of the skill with `# TODO_ADAPT:` markers placed at author-specific points
- A generated `SHAREME.md` following the standard, pre-filled with detected facts
- (with `--sanitize`) author-specific values replaced with `${PLACEHOLDER}` syntax

The original skill is never modified.

You then **review and edit** the generated SHAREME — automation gives you a draft, not a finished doc.

## Use as adopter — `/shareme:unwrap`

When you want to install a skill someone else wrote, ask in plain language:

> "I downloaded this skill at `~/Downloads/their-skill/`, can you help me adopt it?"
>
> or
>
> "I found this skill on github: https://github.com/someone/their-skill — what does it do?"

Or invoke the skill directly:

```
/shareme:unwrap ~/Downloads/their-skill           # local folder
/shareme:unwrap https://github.com/x/their-skill  # github URL (shallow clone)
/shareme:unwrap ~/Downloads/their-skill.zip       # zip file
/shareme:unwrap their-skill                       # already in ~/.claude/skills/
```

Add `--apply` to commit changes (default is dry-run — unwrap shows what it would do and stops):

```
/shareme:unwrap ~/Downloads/their-skill --apply
```

### What happens

In order, unwrap:
1. **Resolves the source** (clone / unzip if needed) and **detects type** (skill vs. plugin).
2. **Runs a decoupled security review** in a subprocess (`claude -p`, `codex exec`, or internal Agent fallback) with a hardened anti-injection prompt. Returns a structured verdict.
3. **Reads `SHAREME.md` if present**; otherwise **infers one** by running the `wrap` analyzer and writes `SHAREME.inferred.md` next to the source with a clear "not authored by the author, inferred from analysis" disclaimer.
4. **Walks `# TODO_ADAPT:` markers interactively**, grouped by category, with full diff preview before any write.
5. **Verifies prerequisites** (binaries on PATH, env vars, dependencies) — refuses to install if anything is missing without your explicit ok.
6. **Installs at the right destination**: `~/.claude/skills/<name>/` for skills, repo-scoped `./.claude/skills/` if you're in a git repo, or the `claude plugin install` command if the source is a plugin.

The trust gate is hard: a red security verdict stops the flow. You can force with `--force` but unwrap insists with a CONFIRM prompt — designed to make accidental override impossible.

## Adopt manually (without `unwrap`)

If you cannot or do not want to use `/shareme:unwrap`, the manual flow still works:

1. Look for a `SHAREME.md` in the skill folder. If it is missing, ask the author to add one (or run `/shareme:wrap` on it yourself).
2. Read sections 4 (behind the scenes) and 9 (cyber warnings) first. Decide whether you are willing to run what the skill does.
3. Read section 5 (author-specific) to understand what you'll need to change.
4. Answer section 7 (onboarding questions) honestly.
5. Then, and only then, adapt and install.

## Why this exists

Every skill I write is shaped by my workspace, my brand, my paths, my corner cases. A skill that works perfectly for me might fail loudly — or worse, silently — in your environment. Or it might do something you didn't expect and didn't want.

Copy-pasting it into your `~/.claude/` folder skips the part where you decide whether the skill fits your problem at all. SHAREME makes that decision visible, structured, and unavoidable.

## Status

**v0.1.0 — Initial release** (first public, tagged version). The standard is usable as-is. `/shareme:wrap` is fully functional. `/shareme:unwrap` ships at design + docs level — the SKILL.md, SHAREME.md, and operational reference are in place; scripts (security review subprocess, marker resolution, install) follow in a later phase. The surface is intentionally small while the spec stabilises toward v1.0. Feedback is welcome — please [open an issue](https://github.com/maxturazzini/aimax-marketplace/issues) for bugs, gaps, or proposals.

## License

MIT. See [`LICENSE`](LICENSE).
