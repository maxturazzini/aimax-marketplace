# modalita-fastidio

**Annoyance mode.** A skill that changes how your assistant works for the rest of the session: fewer words, more finished work.

It exists because a capable model still writes a middle-school essay when you asked whether the test passed. This skill is the written instruction to stop.

## Install

```bash
claude plugin marketplace add maxturazzini/aimax-marketplace
claude plugin install modalita-fastidio@aimax-marketplace
```

## Use

```
/modalita-fastidio
```

From that point on, for the rest of the session, six rules apply.

| # | Rule | In one line |
|---|---|---|
| 0 | Be understood | What arrives on the other side is what counts. Beats every other rule. |
| 1 | Done means done | Five things asked, five things delivered. |
| 2 | Act, don't ask | Permission only for what reaches a person, what can't be undone, what costs a lot. |
| 3 | A question is a question | "Should we use X?" does not mean "migrate everything to X". |
| 4 | Go fast | Parallelize, delegate routine work, don't idle waiting. |
| 5 | Short answers | Simple words, short sentences, one idea per sentence. |

Every reply opens with a one-line joke confirming the mode is on. When the line disappears, the skill has fallen out of context and you retype the command. The joke is the alarm.

## Language

The skill ships in **Italian**. An English variant is in
[`skills/modalita-fastidio/references/SKILL.en.md`](skills/modalita-fastidio/references/SKILL.en.md) —
replace `SKILL.md` with it to run the mode in English.

## Adopt it consciously

Read [`SHAREME.md`](skills/modalita-fastidio/SHAREME.md) before installing. Five minutes.
Every author-specific point is marked in the source:

```bash
grep -rn "TODO_ADAPT:" .
```

## License

MIT. See the repo [`LICENSE`](../../LICENSE).
