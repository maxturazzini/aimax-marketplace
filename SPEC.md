# SHAREME.md — Specification v0.1

A `SHAREME.md` is a companion file that lives next to a `SKILL.md` whenever a skill leaves its author's workspace.

It is not a marketing pitch. It is a contract for conscious adoption.

## Why SHAREME exists

Installing a skill from someone else's environment without reading what it does is reckless. Even when a skill has no obvious customizations (paths, brand, profiles, naming), it still does things — it writes files, makes network calls, calls MCP servers, depends on tools, assumes runtimes.

The adopter has the right and the duty to know **what** before deciding **whether**.

`SHAREME.md` makes that information explicit, structured, and readable in five minutes.

## Required sections

A compliant `SHAREME.md` MUST include the following sections, in this order, with these exact headings.

### 1. What this is

One or two lines. What the skill does, no marketing.

### 2. What I can do

Concrete capabilities. Each one with one short example of invocation or output.

### 3. What I do NOT do

Explicit limitations. The boundary of competence.

### 4. What I do behind the scenes

Side effects that may not be obvious from the SKILL.md:
- Network calls (which domains, which endpoints)
- File system writes outside the skill folder
- External services touched (APIs, MCP servers, OS integrations)
- Persistent state (browser profiles, caches, databases)
- Anything the adopter would want to audit before installing

### 5. What is author-specific

A table with columns: **What** / **Where** / **Why** / **How to change**.

Lists every element of the skill that was tailored to its original author and would need to be changed to fit a different context. Examples: hardcoded paths, brand mentions, naming conventions, viewport sizes, account references.

### 6. What you might do with it

Three to five alternative use cases beyond the original. Helps the adopter see whether the skill fits their actual problem, or whether it is the wrong shape.

### 7. Onboarding questions

A checklist of questions the adopter must answer **before** touching code. Examples:
- What problem are you trying to solve?
- What is your equivalent of `${COURSE_ROOT}` in your environment?
- Do you already have the prerequisites listed in section 8?

The skill is not adopted until these are answered. The list belongs to the adopter, not to the author.

### 8. Technical prerequisites

Runtime versions, Python/Node/etc. dependencies, OS permissions, accounts, tokens. Anything that must exist before the skill can run.

### 9. Cyber and security warnings

Credentials, persistent profiles, terms-of-service implications, data leakage risks. Be specific. "Stores cookies in `~/.skill-profile/`" is useful. "Be careful with security" is not.

### 10. How to adapt

Step-by-step flow for adapting the skill to a new context. No time promises — adaptation time depends on the skill and on the adopter.

### 11. License and disclaimer

License terms. Warranty disclaimer. Attribution rules. How to reach the original author with bugs or questions.

## Optional sections

These MAY be included when relevant.

- **Provenance** — who wrote it, in what context, with what assumptions
- **Alternatives** — similar skills, why this one is different
- **Roadmap** — direction of future evolution (no promises)
- **Changelog** — version history of the SHAREME.md itself

## Format conventions

See [CONVENTIONS.md](CONVENTIONS.md) for placeholder syntax, adapt markers, file naming, and tone guidelines.

## Compliance

A skill is "SHAREME-compliant" when:

1. A file named `SHAREME.md` exists at the root of the skill folder (next to `SKILL.md`)
2. All eleven required sections are present, in order, with the exact headings above
3. The "What I do behind the scenes" section is non-empty (writing "nothing" is a valid answer if true, but the section must be addressed)
4. Author-specific elements are explicitly listed in section 5, even when none exist
5. The license section is filled in, even if just to point at the repo's `LICENSE` file

## Versioning

This spec follows semantic versioning. Breaking changes to required sections increment the major version. Adding optional sections increments the minor version. Editorial changes increment the patch version.

Current: **v0.1.0** (draft).
