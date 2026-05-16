# Conventions

Format rules for SHAREME-compliant skills.

## Placeholders

When the original skill contained author-specific values that the adopter must change, use placeholders in the depersonalized copy.

**Syntax**: `${VARIABLE_NAME}` — uppercase, snake_case, surrounded by `${...}`.

**Examples**:

| Original (author-specific) | Placeholder | Description (in SHAREME.md section 5) |
|---|---|---|
| `/Users/maxturazzini/courses/python/` | `${COURSE_ROOT}` | Root folder where course materials live |
| `~/.uc-chatgpt-profile` | `${BROWSER_PROFILE_DIR}` | Persistent Chrome profile for automation |
| `1024x768` | `${VIEWPORT_SIZE}` | Recording viewport, must match brand video format |
| `corsi/{name}/` | `${PROJECT_LAYOUT}` | Folder structure for projects |

Every placeholder used in the skill MUST be documented in section 5 ("What is author-specific") of the SHAREME.md, with a clear explanation of what to substitute.

## Adapt markers in code

When code contains a value that may need changing, but the value cannot be cleanly extracted into a placeholder (e.g., it is interleaved with logic, or there are multiple plausible substitutions), mark it with a comment.

**Syntax**: `# TODO_ADAPT: <description>` (or the comment syntax of the relevant language).

**Example** (Python):
```python
viewport = (1024, 768)  # TODO_ADAPT: choose viewport matching your video format
profile_dir = os.path.expanduser("~/.uc-chatgpt-profile")  # TODO_ADAPT: pick a dedicated profile path
```

**Example** (YAML):
```yaml
output_path: corsi/${COURSE_NAME}/videos/  # TODO_ADAPT: align with your folder layout
```

Adopters can find every adaptation point with one command:
```bash
grep -rn "TODO_ADAPT:" .
```

## File naming

- The companion file MUST be named exactly `SHAREME.md` — uppercase, no extension variants.
- It MUST live at the root of the skill folder, next to `SKILL.md`.
- Do not name it `SHARE-ME.md`, `shareme.md`, `README-SHARE.md`, etc.

## Tone

The SHAREME.md is a contract, not a brochure.

- **Declarative** over promotional. State what is, not how good it is.
- **Specific** over vague. "Stores cookies in `~/.profile/`" beats "handles authentication".
- **No marketing language**. No "powerful", "easy-to-use", "seamless", "robust".
- **No implicit warranties**. Avoid words that imply guarantees ("always works", "never fails").
- **Plain English**. Translate jargon when first introduced.
- **Active voice**. "The skill writes a log file" beats "A log file is written".

## Length

A SHAREME.md should be readable in five minutes. Aim for 2-4 KB of prose. If a section grows longer than half a screen, consider whether it really belongs there or in the SKILL.md / a separate doc.

## What does NOT belong in SHAREME.md

- **Tutorials** — those go in `references/` or a separate doc.
- **Architecture deep-dives** — link out to a `docs/` folder if needed.
- **Personal stories** — keep them in blog posts, not in adoption contracts.
- **Marketing copy** — see "Tone".
- **Roadmap promises** — the optional roadmap section is for direction, not commitments.
