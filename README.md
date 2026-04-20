# xmp4

> Semantic code intelligence MCP server for AI agents.
> **Free hosted endpoint**: `mcp.example4.ai`

xmp4 gives AI coding agents (Claude Code, Cursor, Claude Desktop, Continue, Windsurf) semantic access to **547+ popular open-source libraries** — pre-indexed via SCIP, navigable through MCP. Find symbols, usages, call graphs, type hierarchies across React, Django, Spring Boot, Tokio, Vercel AI SDK, and hundreds of others.

**81–87% fewer tokens** than grep-based approaches ([benchmark](https://github.com/LadislavSopko/lsai-protocol/blob/master/RESULTS.md)).

🚧 **This repo is being set up.** Full docs landing here over the next few days. Source code is private at [0ics-srls/lsai-xmp4](https://github.com/0ics-srls/lsai-xmp4); this repo hosts user-facing docs, install instructions, and the public issue tracker.

## Quick start (preview)

```jsonc
// Claude Code: ~/.config/claude/mcp.json
{
  "mcpServers": {
    "xmp4": {
      "url": "https://mcp.example4.ai",
      "transport": "http"
    }
  }
}
```

Full setup guides for each client coming in `docs/`.

## Status

- ✅ Server live at `mcp.example4.ai` (v1.1.3, 547 repos, 9145 projects, 17 MCP tools)
- 🔧 Public docs (this repo) — in progress
- 🔧 Submission to MCP registries — in progress
- 🔧 Demand-driven repo growth from aggregate query logs — in progress

## License

Apache 2.0 — see [LICENSE](LICENSE).

## Issues

Found a bug? Want a library indexed that we don't have?
→ [Open an issue](https://github.com/0ics-srls/lsai-xmp4.public/issues/new/choose)
