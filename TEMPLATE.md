# SHAREME — `<skill-name>`

> Companion document to `SKILL.md`. Read this **before** installing or running the skill.

## 1. What this is

<One or two lines. What this skill actually does.>

## 2. What I can do

- **<Capability 1>** — <one-line description>
  Example: `<example invocation or input>`
- **<Capability 2>** — <one-line description>
  Example: `<example>`
- **<Capability 3>** — <one-line description>
  Example: `<example>`

## 3. What I do NOT do

- <Thing the skill does not handle>
- <Thing that is out of scope>
- <Thing the adopter might wrongly assume is included>

## 4. What I do behind the scenes

The adopter has the right to know what runs when this skill is invoked. List everything that is not obvious from `SKILL.md`.

- **Network calls**: <none, or list domains/endpoints>
- **File system writes**: <inside skill folder only, or list paths outside>
- **External services**: <none, or list APIs / MCP servers / OS integrations>
- **Persistent state**: <none, or describe browser profiles, caches, databases>
- **Tools used**: <list shell commands, binaries, system tools>

If a category genuinely doesn't apply, write "none". Don't omit the line.

## 5. What is author-specific

| What | Where | Why | How to change |
|---|---|---|---|
| `<element>` | `<file:line or path>` | <reason author chose this value> | <what to replace it with> |
| `<element>` | `<file:line or path>` | <reason> | <how to adapt> |

If the skill has no author-specific elements, write a single row: `none | — | — | —` and explain in one line why (e.g., "skill is fully parametrized via CLI flags").

## 6. What you might do with it

Beyond the original use case, here are alternative scenarios:

- **<Use case A>** — <how to apply the skill>
- **<Use case B>** — <how to apply>
- **<Use case C>** — <how to apply>

## 7. Onboarding questions

Answer these before touching code:

1. <Question about your context — e.g., "What is your equivalent of `${COURSE_ROOT}`?">
2. <Question about target output — e.g., "Public-facing or internal-only?">
3. <Question about scale — e.g., "How many runs per week?">
4. <Question about prerequisites — e.g., "Do you have `<dependency>` installed?">
5. <Question about constraints — e.g., "Are you allowed to automate `<service>` under its ToS?">

## 8. Technical prerequisites

- **Runtime**: <Python 3.x, Node X, etc.>
- **OS**: <macOS / Linux / Windows / cross-platform>
- **Dependencies**: <list, with versions if relevant>
- **OS permissions**: <e.g., screen recording, accessibility>
- **Accounts and tokens**: <list services and what kind of access>

## 9. Cyber and security warnings

- <Specific risk 1 — e.g., "Stores session cookies in `~/.profile-name/`. Do not commit or share.">
- <Specific risk 2 — e.g., "Sends data to `<service>`. Verify it is acceptable under your data policy.">
- <ToS or legal consideration if relevant>

Be specific. Vague warnings are useless.

## 10. How to adapt

1. Read sections 4 and 5 of this file
2. Answer the onboarding questions in section 7
3. Install prerequisites from section 8
4. <Specific step — e.g., "Replace `${COURSE_ROOT}` everywhere with your path">
5. <Specific step — e.g., "Grep for `TODO_ADAPT:` and address each marker">
6. <Verification step — e.g., "Run `<command>` to validate the setup">

## 11. License and disclaimer

- **License**: <MIT / Apache 2.0 / proprietary, see `LICENSE`>
- **Warranty**: none. Use at your own risk.
- **Attribution**: <how to credit the original author, if required>
- **Contact**: <email / GitHub issues / other>

---

## Optional sections

### Provenance

<Who wrote this, in what context, with what assumptions.>

### Alternatives

<Similar skills or tools, why this one is different.>

### Roadmap

<Direction of future evolution. No promises.>

### Changelog

- v0.1.0 — initial release
