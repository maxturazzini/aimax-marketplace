# Contributor instructions — aimax-marketplace marketplace

This repo is a **Claude Code marketplace**, not a single plugin. Users register the marketplace once (`claude plugin marketplace add maxturazzini/aimax-marketplace`) and then install any plugin from it.

## Layout

```
.claude-plugin/marketplace.json   Marketplace catalog (name, plugins[])
README.md                          Marketplace-level docs (this is the entry point)
LICENSE                            Repo-wide license (plugins may override)
plugins/
  <plugin-name>/
    .claude-plugin/plugin.json   Plugin manifest
    README.md                     Plugin-specific docs
    CLAUDE.md                     Plugin-specific contributor notes (if any)
    SKILL files, scripts, etc.
```

## Adding a new plugin

1. Create `plugins/<plugin-name>/` and put the plugin source inside (including its own `.claude-plugin/plugin.json`).
2. Add an entry to `.claude-plugin/marketplace.json` under `plugins[]` with `"source": "./plugins/<plugin-name>"`.
3. Add a row to the **Plugins** table in the root `README.md`.
4. Commit and push. Users get the new plugin after `claude plugin marketplace update aimax-marketplace`.

## Invariants

- **Marketplace name is `aimax-marketplace`** in `marketplace.json` and in all install instructions. The plugin name lives inside `plugins[].name` and is independent.
- **Each plugin is self-contained** in its `plugins/<name>/` folder. Plugin internals (paths, scripts) must use paths relative to the plugin folder, not the repo root.
- **Per-plugin contributor notes** live in `plugins/<name>/CLAUDE.md` and `plugins/<name>/README.md`. Do not promote plugin-specific details into root files.

## THE SHAREME CONTRACT — most important rule

Every plugin in this marketplace, **except `shareme` itself**, must satisfy this contract. No exceptions. If a plugin doesn't meet all three points, it does not belong here.

1. **Works out of the box.** Installing the plugin with defaults must produce a functioning skill. No "edit before first run" is allowed. Real plug & play, not plug & pray.
2. **Ships with a `SHAREME.md` companion** next to its `SKILL.md` (or equivalent entry point), following the [SHAREME spec](plugins/shareme/SPEC.md). The companion documents what the plugin does behind the scenes, what's author-specific, and what an adopter would want to change to make it theirs.
3. **Carries `# TODO_ADAPT:` markers** in the source at every author-specific point — paths, brand voice, named entities, defaults that depend on the author's setup. Adapting must be search-and-replace, not forensic reading.

To produce a compliant SHAREME and place the markers automatically, run `/shareme:wrap` (the plugin in this marketplace) against your plugin folder before adding it to `plugins/`. Then edit the prose-heavy SHAREME sections by hand.

**`shareme` is the exception** because it's the meta-tool that enforces this contract for the others. By design, `shareme` itself is **hard** — minimal customization surface, no brand voice, no environment-specific defaults — because a rigid tool is what makes the rest of the marketplace soft and adaptable. Do not "soften" `shareme` to make it more personal; that would defeat its purpose.

## Commit identity

This repo uses identity `maxturazzini / max@turazzini.com` for commits. Verify with `git config user.name` before committing if in doubt. Do not change global git config — set it locally for this repo.
