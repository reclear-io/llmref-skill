# llmref skill

A [Claude Code](https://claude.com/claude-code) / Claude Agent **skill** that
teaches an assistant to fetch **version-pinned** documentation for any library,
framework, SDK, API, or CLI from the [LLM Reference](https://llmref.org) registry
(`api.llmref.org`) instead of relying on training data.

The point is version-correctness: it resolves the exact version a project uses
and reads *that* snapshot's docs, so answers don't drift to whatever version the
model happened to absorb. It prefers the `llmref` MCP server when connected, and
otherwise falls back to plain `curl` against the public API — no account, API
key, or install required.

> This repo is the packaged, installable form of the skill that lives at
> [`reclear-io/llmref/integrations/claude-skill`](https://github.com/reclear-io/llmref/tree/main/integrations/claude-skill).

## Install

The repository root *is* the skill (`SKILL.md` lives at the top level), so
installing is just placing it in a directory Claude Code discovers.

### Quick install (recommended)

```sh
# Personal — available in every project
git clone https://github.com/reclear-io/llmref-skill ~/.claude/skills/llmref

# …or per-project — checked in with the repo
git clone https://github.com/reclear-io/llmref-skill .claude/skills/llmref
```

### One-liner

```sh
curl -fsSL https://raw.githubusercontent.com/reclear-io/llmref-skill/main/install.sh | sh
```

Installs into `~/.claude/skills/llmref` by default. Override the target:

```sh
# per-project install
LLMREF_SKILL_DIR=.claude/skills/llmref \
  sh -c "$(curl -fsSL https://raw.githubusercontent.com/reclear-io/llmref-skill/main/install.sh)"
```

### Manual copy

Download and drop the `SKILL.md` + `references/` into
`~/.claude/skills/llmref/` (or `.claude/skills/llmref/`) yourself. Any layout
where Claude Code finds `<skills-dir>/llmref/SKILL.md` works.

## Verify

Restart or reload Claude Code and check the skill is discovered:

```sh
claude skills          # or: /skills inside an interactive session
```

Then ask about any indexed library, e.g. *"look up the Drizzle docs for
0.45.2"* or *"how do I configure caching in Next.js"* — the skill resolves the
version and pulls the docs.

## Optional: connect the MCP server for cleaner tool calls

The skill works standalone via `curl`, but if you connect the `llmref` MCP
server it will prefer the structured tools (`list_projects`, `list_versions`,
`resolve_docs`, `search_docs`):

```sh
claude mcp add --transport http llmref https://api.llmref.org/v1/mcp

# with an API key for higher rate limits (never required for data):
claude mcp add --transport http llmref https://api.llmref.org/v1/mcp \
  --header "Authorization: Bearer your-key-here"
```

## Update

```sh
git -C ~/.claude/skills/llmref pull
```

## Uninstall

```sh
rm -rf ~/.claude/skills/llmref
```

## Contents

| Path | What it is |
|---|---|
| `SKILL.md` | Trigger conditions, surface priority (MCP → curl → SDK/CLI), and the discover → resolve → read/search workflow. |
| `references/api-reference.md` | Full HTTP API, MCP tools, `@llmref/cli`, and `@llmref/sdk` surface. |
| `install.sh` | Clones (or copies) the skill into your Claude skills directory. |

## Links

- Registry & API: <https://llmref.org> · `https://api.llmref.org/v1`
- Main project: <https://github.com/reclear-io/llmref>

## License

[MIT](./LICENSE) © Reclear
