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

```bash
claude /plugin install https://github.com/maxturazzini/shareme
```

The skill becomes available as `/shareme:generate`.

## Use

Generate a shareable copy of a skill you authored:

```
/shareme:generate my-cool-skill
```

This creates `my-cool-skill_shared/` next to the original — a sibling folder containing:
- A copy of the skill with `# TODO_ADAPT:` markers placed at author-specific points
- A generated `SHAREME.md` following the standard
- (with `--sanitize`) author-specific values replaced with `${PLACEHOLDER}` syntax

The original skill is never modified.

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
