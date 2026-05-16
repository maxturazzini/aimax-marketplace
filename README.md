# aimax-skills

**Claude Code marketplace by Max Turazzini.** Add the marketplace once, install plugins on demand, get updates as new ones land.

## The plug & play contract

A plugin written by someone else carries three things into your environment, not one:

1. **Their setup** — paths, brand voice, tool choices, file conventions.
2. **Their way of thinking** — the framing they imposed on the problem, the defaults they considered obvious, the trade-offs they made without writing them down.
3. **The slop of the AI that helped write it.** Most plugins in circulation today are largely auto-generated. Whatever quirks, verbosity, and assumptions the model carried at generation time are baked in — and drift further with every iteration unless someone reins them in.

The honest verb for ignoring all three and just running the thing is **`plug & pray`**. Not a verb you want in a working session.

So every plugin in `aimax-skills` is held to a contract:

- **Works out of the box** with sensible defaults — real plug & play, not plug & pray.
- **Ships with a `SHAREME.md` companion** that names, in 5 minutes of reading, what the plugin does behind the scenes, what's author-specific, and what you'd want to change to make it yours.
- **Carries `# TODO_ADAPT:` markers** in the source at every author-specific point, so adapting is a search, not a forensic read.

> Use it as-is. Then adapt when you're ready.

**The fun part:** [`shareme`](plugins/shareme/) — the plugin that produces companions and markers for everything else — is deliberately **hard**. Minimal customization surface, generic by design. The one rigid tool is what lets every other skill in this marketplace be soft.

## Install the marketplace

```bash
claude plugin marketplace add maxturazzini/aimax-skills
```

This registers the repo as a marketplace. You only do it once.

## Browse and install plugins

```bash
claude plugin marketplace browse aimax-skills      # list available plugins
claude plugin install <plugin-name>@aimax-skills   # install a specific one
```

## Plugins

| Plugin | What it does |
|---|---|
| [`shareme`](plugins/shareme/) | Generates SHAREME.md companion documentation for any Claude Code skill — the standard for adopting skills consciously. |

_More to come. The marketplace grows over time; run `claude plugin marketplace update aimax-skills` to see new additions._

## Update

```bash
claude plugin marketplace update aimax-skills   # refresh the marketplace catalog
claude plugin update <plugin-name>              # update a specific installed plugin
```

## Try a plugin without installing

```bash
git clone https://github.com/maxturazzini/aimax-skills.git
claude --plugin-dir ./aimax-skills/plugins/<plugin-name>
```

## License

MIT. See [`LICENSE`](LICENSE).

You can fork, modify, redistribute, and use this commercially. The only requirement: **keep the copyright notice** (`Copyright (c) 2026 Max Turazzini`) in your copies or derivatives. Attribution is the price; everything else is yours.

Individual plugins may declare their own license in their manifest.
