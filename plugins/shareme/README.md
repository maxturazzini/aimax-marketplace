# SHAREME

**A standard for sharing Claude Code skills consciously.**

Installing a skill from someone else's environment without reading what it does is reckless. Even when a skill has no obvious customizations, it still does things. It writes files, makes network calls, depends on tools, assumes runtimes. The adopter has the right and the duty to know **what** before deciding **whether**.

`SHAREME.md` is a companion file that lives next to a skill's `SKILL.md` and answers, in five minutes of reading, the questions that should never be skipped.

> Skills are adopted, not magically installed. Unless you enjoy risking your context window.

## What you get

This repository contains:

1. **The standard** — [`SPEC.md`](SPEC.md) defines the eleven sections every SHAREME.md must include.
2. **A boilerplate** — [`TEMPLATE.md`](TEMPLATE.md) you can copy and fill in for your own skill.
3. **Conventions** — [`CONVENTIONS.md`](CONVENTIONS.md) for placeholders, adapt markers, naming, tone.
4. **A working example** — [`examples/example-shareme.md`](examples/example-shareme.md).
5. **A Claude Code skill** — `/shareme:generate`, which produces a SHAREME-compliant copy of any skill you point it at.

## Install

`shareme` lives inside the **aimax-skills** marketplace. You register the marketplace once, then install any plugin from it on demand:

```bash
# 1. Register the marketplace (once)
claude plugin marketplace add maxturazzini/aimax-skills

# 2. Install the shareme plugin from it
claude plugin install shareme@aimax-skills
```

The first command clones the marketplace repo into `~/.claude/plugins/marketplaces/aimax-skills/`. The second installs `shareme`. The skill becomes available as `/shareme:generate` in any Claude Code session.

### Verify

```bash
claude plugin list
```

You should see `shareme` in the output. In a Claude Code session, typing `/shareme:` should suggest `generate` as available.

### Update later

```bash
claude plugin marketplace update aimax-skills   # pulls latest changes (also shows newly added plugins)
claude plugin update shareme                     # applies updates to shareme (restart required)
```

### Uninstall

```bash
claude plugin uninstall shareme
# (leave the marketplace registered if you have other aimax-skills plugins installed)
claude plugin marketplace remove aimax-skills
```

### Try it without installing (development / one-shot)

To test a local clone or a fork without going through the marketplace:

```bash
git clone https://github.com/maxturazzini/aimax-skills.git
claude --plugin-dir ./aimax-skills/plugins/shareme
```

The plugin is loaded for that single Claude Code session only.

## Use

In a Claude Code conversation, ask in plain language:

> "Prepare my `weather-bot` skill for sharing — generate a SHAREME for it."

Or invoke the skill directly:

```
/shareme:generate weather-bot
```

Or pass an absolute path if your skills don't live in `~/.claude/skills/`:

```
/shareme:generate path:/Users/me/projects/my-skill
```

Add `--sanitize` to also replace detected author-specific values with `${PLACEHOLDER}` syntax in the copy:

```
/shareme:generate weather-bot --sanitize
```

### What happens

The skill creates a sibling folder `weather-bot_shared/` next to the original, containing:
- A copy of the skill with `# TODO_ADAPT:` markers placed at author-specific points
- A generated `SHAREME.md` following the standard, pre-filled with detected facts
- (with `--sanitize`) author-specific values replaced with `${PLACEHOLDER}` syntax

The original skill is never modified.

You then **review and edit** the generated SHAREME — automation gives you a draft, not a finished doc.

## Adopt a skill yourself

When you want to install a skill someone else wrote:

1. Look for a `SHAREME.md` in the skill folder. If it is missing, ask the author to add one (or run `/shareme:generate` on it yourself).
2. Read sections 4 (behind the scenes) and 9 (cyber warnings) first. Decide whether you are willing to run what the skill does.
3. Read section 5 (author-specific) to understand what you'll need to change.
4. Answer section 7 (onboarding questions) honestly.
5. Then, and only then, adapt and install.

## Why this exists

Every skill I write is shaped by my workspace, my brand, my paths, my corner cases. A skill that works perfectly for me might fail loudly — or worse, silently — in your environment. Or it might do something you didn't expect and didn't want.

Copy-pasting it into your `~/.claude/` folder skips the part where you decide whether the skill fits your problem at all. SHAREME makes that decision visible, structured, and unavoidable.

## Status

**v0.1.0** — early draft. The spec is open to feedback. Open an issue if you have one.

## License

MIT. See [`LICENSE`](LICENSE).
