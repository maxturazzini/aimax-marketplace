# Internal workflow reference for `/shareme:generate`

This document is for Claude when invoking the skill. It captures the operational
sequence and the judgment calls expected during execution.

## Inputs

The user invokes one of:

- `/shareme:generate <skill-name>`
- `/shareme:generate path:/abs/path/to/skill`
- `/shareme:generate <skill-name> --sanitize`

## Resolution

1. If the invocation specifies a path: use it directly.
2. If it specifies a name: resolve as `~/.claude/skills/<name>/`. If that does not exist, ask the user for the path explicitly. Do not guess.

## Plugin paths

The skill lives at `<plugin_root>/skills/generate/`. The standard files are at the plugin root:

- `<plugin_root>/SPEC.md`
- `<plugin_root>/TEMPLATE.md`
- `<plugin_root>/CONVENTIONS.md`

Relative path from the skill scripts folder: `../../`. Use the absolute path when invoking helper scripts to avoid ambiguity.

## Execution sequence

1. **Validate target**: confirm the target directory exists and contains a `SKILL.md`. If not, abort with a clear message.

2. **Analyze**: run

   ```
   python <plugin_root>/skills/generate/scripts/analyze_skill.py <target_path> --output <tmp>/analysis.json
   ```

3. **Review with user**: read the analysis output and walk the user through:
   - Detected author-specific paths (confirm or ignore each)
   - Detected network calls (any unexpected domains?)
   - Detected MCP servers / external tools
   - Python dependencies

   Ask before tagging brand names or ambiguous strings as author-specific.

4. **Generate SHAREME.md**: run

   ```
   python <plugin_root>/skills/generate/scripts/generate_shareme.py \
       --analysis <tmp>/analysis.json \
       --template <plugin_root>/TEMPLATE.md \
       --output <target_parent>/<target_name>_shared/SHAREME.md
   ```

5. **Copy and mark**: run

   ```
   python <plugin_root>/skills/generate/scripts/sanitize_skill.py \
       <target_path> <target_parent>/<target_name>_shared \
       --analysis <tmp>/analysis.json [--sanitize]
   ```

6. **Report to user**:
   - Show the output folder structure
   - Show the first 30 lines of the generated `SHAREME.md`
   - List every section that still contains `<TODO: ...>` markers
   - Remind: automation is a draft. Review every section before sharing.

## Judgment calls expected from Claude

- **Brand detection**: regex won't catch this. When the analysis flags repeated capitalized terms or uncommon proper nouns, ask the user whether they are author-specific brand mentions.
- **Capability descriptions**: the script puts the SKILL.md `description` field into section 1, but section 2 ("What I can do") needs prose. Read the SKILL.md and write 3-5 capability bullets based on what the skill actually does.
- **Onboarding questions**: section 7 must be tailored to the skill's domain. Generic questions ("what's your runtime") are useless. Read the analysis and propose 4-6 questions that actually matter for this skill's adoption.
- **Cyber warnings**: be specific. If the skill writes browser cookies, say so and name the path. If it sends data to a public API, name the API.

## Failure modes

- **Target has no `SKILL.md`**: abort and tell the user.
- **Target folder name conflict**: if `<target>_shared/` already exists, ask the user whether to overwrite or pick a new suffix.
- **Analysis file fails to write**: probably permission. Use `/tmp/` as a fallback.
- **Template missing**: the plugin install is broken. Tell the user to reinstall.
