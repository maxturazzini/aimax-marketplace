# SHAREME.md — modalita-fastidio

Companion for conscious adoption. SHAREME spec v0.1.

## 1. What this is

A prompt-only skill that changes the assistant's working behavior for the rest
of the session: be understood, finish what was asked, act instead of asking
permission, answer questions without implementing them, go fast, keep replies
short. It contains no code.

## 2. What I can do

- **Cut verbosity.** Replies become short and structured: what was done, whether
  it worked, what you do next. Example: `/modalita-fastidio` then "does the test
  pass?" returns two lines instead of three approaches with trade-offs.
- **Reduce permission questions.** Reversible, cheap work happens and gets
  reported. Asking is reserved for three named cases.
- **Stop over-implementation.** "Should we use X?" gets an answer, not a
  migration.
- **Declare its own precedence.** Rule 0 (be understood) beats rule 5 (be
  short), so brevity never wins over clarity.
- **Signal that it is still on.** Every reply opens with a one-line joke. When
  the line stops appearing, the skill has fallen out of context.

## 3. What I do NOT do

- Does not run scripts, commands, or network calls of its own.
- Does not override your project's `CLAUDE.md` or rules. It says so in its own
  first paragraph.
- Does not persist. It lasts one session and dies at context compaction.
- Does not measure anything. There is no telemetry, no token counter, no report.
- Does not change model, temperature, or any harness setting.

## 4. What I do behind the scenes

Nothing mechanical. No network calls, no file writes, no MCP servers, no
external services, no persistent state, no caches. The whole plugin is markdown.

One non-obvious behavioral effect, worth naming: **rule 2 makes the assistant
act without asking** on work it judges reversible and cheap. Files get edited,
searches get run, drafts get written, and you find out afterwards. That is the
point of the skill, and it is also the main thing to weigh before installing.
See section 9.

## 5. What is author-specific

| What | Where | Why | How to change |
|---|---|---|---|
| Italian language | `SKILL.md`, whole file | Written for an Italian-speaking author | Replace `SKILL.md` with `references/SKILL.en.md`, or translate |
| "Italiano facile" / ASD-STE100 | `SKILL.md` rule 5 | Author's readability target | Set your own register in rule 5 |
| The three "ask first" cases | `SKILL.md` rule 2 | Author's irreversible actions are sends and publications | Marked `TODO_ADAPT`. Replace with yours: production deploys, migrations, paid API spend |
| Subagent guidance | `SKILL.md` rule 4 | Author runs a harness that can spawn subagents | Marked `TODO_ADAPT`. Drop the two bullets if yours cannot |
| 🔥 emoji and the six jokes | `SKILL.md` "Segnale" | Author's taste | Marked `TODO_ADAPT`. Rewrite in your tone, or use a neutral `[fastidio on]` |
| Skill name in Italian | folder and `plugin.json` | Original name | Renaming means editing the frontmatter `name`, the folder, and the manifest |

Find every marker with `grep -rn "TODO_ADAPT:" .`

## 6. What you might do with it

- **A reviewer mode** where the assistant reports findings and never edits, by
  inverting rule 2.
- **A pair-programming mode** for a language you are learning, keeping rule 0
  and rule 5 and dropping the rest.
- **A house style for a team**, with rule 5 rewritten as your documentation
  register so every assistant in the team answers the same way.
- **An on-call mode**, where rule 2's three cases become your incident
  boundaries and rule 4 disappears entirely.
- **A teaching aid**: the file is short enough to read aloud and argue with,
  which makes it a decent artifact for a workshop on how instructions shape
  model behavior.

## 7. Onboarding questions

Answer these before installing.

- What does "irreversible" mean in your environment? Name three concrete actions.
- Are you comfortable with the assistant editing files and then telling you?
- What language do you want your replies in?
- Do you have a project `CLAUDE.md` whose rules could conflict with rule 2?
- Who else works in this repo, and would they expect to be asked first?

## 8. Technical prerequisites

Claude Code with plugin support. Nothing else. No runtime, no dependencies, no
accounts, no tokens, no OS permissions.

## 9. Cyber and security warnings

No credentials are stored, read, or transmitted. The plugin has no code path.

The real risk is behavioral, and it is worth stating plainly. Rule 2 lowers the
rate at which the assistant asks for confirmation. In a session that already has
broad tool permissions, that means more file edits and more commands run before
you see them. The skill draws its own line at "reaches a person, cannot be
undone, costs a lot", but the assistant is the one judging which side an action
falls on, and it can misjudge.

Two mitigations, both outside this plugin: keep your permission settings
restrictive, and work on a branch. Do not pair this skill with a
`bypassPermissions` session unless you accept unreviewed changes.

## 10. How to adapt

1. Read `SKILL.md` end to end. It is 120 lines and it is the whole product.
2. Choose your language. Keep `SKILL.md`, or copy `references/SKILL.en.md` over it.
3. `grep -rn "TODO_ADAPT:" .` and work through each marker.
4. Rewrite rule 2's three cases with your real irreversible actions. This is the
   marker that matters most.
5. Rewrite the signal lines in your own tone, or drop the emoji.
6. Run one real session with it. If the assistant asked you something it should
   have decided, that is a rule 2 problem. If it did something it should have
   asked about, that is also a rule 2 problem, in the other direction. Tune the
   three cases, not the whole file.

## 11. License and disclaimer

MIT. See the repository `LICENSE`. Keep the copyright notice
(`Copyright (c) 2026 Max Turazzini`) in copies and derivatives.

Provided as is, without warranty of any kind. A skill that reduces confirmation
prompts shifts risk onto you: you are responsible for what your assistant does
in your repository.

Issues and questions: https://github.com/maxturazzini/aimax-marketplace/issues
