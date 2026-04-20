# xmp4 — Semantic Code Intelligence MCP

> **Free hosted endpoint**: `https://mcp.example4.ai/mcp`
> **Transport**: MCP Streamable HTTP
> **Status**: v1.1.3, production

xmp4 is an MCP (Model Context Protocol) server that gives AI coding assistants — Claude Code, Cursor, Claude Desktop, Continue, Windsurf — **semantic** access to popular open-source libraries. Instead of scraping files through `grep`, your AI reads the **SCIP-indexed symbol graph** of 547 + pre-indexed repositories across 10 languages: find the definition, every caller, every implementation, the exact method body — in a single tool call.

No install. No API key for the public endpoint. No access to your code — xmp4 only reads OSS it has already indexed.

## What's here

| File | Purpose |
|---|---|
| [`docs/connect-instructions.md`](docs/connect-instructions.md) | Configuration snippets for Claude Code, Cursor, Claude Desktop, Continue, Windsurf |
| [`docs/tool-reference.md`](docs/tool-reference.md) | 17 MCP tools, prescribed workflow, live examples, known limitations |
| [`docs/tiers-and-quirks.md`](docs/tiers-and-quirks.md) | Tier-1 / tier-2 language guarantees, per-language indexer behavior |
| [`docs/privacy.md`](docs/privacy.md) | What we log, what we don't, open-stats endpoint |
| [`docs/request-repo.md`](docs/request-repo.md) | How to get a library added to the index (opens an issue here) |
| [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/) | Bug, feature-request, request-repo templates |

The server source is private at [`0ics-srls/lsai-xmp4`](https://github.com/0ics-srls/lsai-xmp4); this repository hosts **only user-facing documentation, issue tracking, and the repo-request intake**.

## 30-second setup — Claude Code example

`~/.claude/mcp.json`:

```jsonc
{
  "mcpServers": {
    "xmp4": {
      "transport": { "type": "http", "url": "https://mcp.example4.ai/mcp" }
    }
  }
}
```

Restart Claude Code. Then try (every step verified live 2026-04-20):

> *"Using xmp4, call xmp4_guide first, then find the Flask class in flask/Flask and list its usages."*

You should see: the workflow guide, `Type Flask src/flask/app.py:81`, and 165 usages across 33 result pages — one call per question, no grep loops.

Full setup for Claude Code, Cursor, Claude Desktop, Continue, and Windsurf in [`docs/connect-instructions.md`](docs/connect-instructions.md).

## The 17 tools at a glance

Three groups, the first is where the value lives:

**Core semantics** — `xmp4_projects`, `xmp4_search`, `xmp4_info`, `xmp4_usages`, `xmp4_callers`, `xmp4_callees`, `xmp4_hierarchy`, `xmp4_outline`, `xmp4_source`, `xmp4_tests_for`, `xmp4_deps`, `xmp4_symbol_at`

**Convenience** — `xmp4_view` (raw file excerpt), `xmp4_grep` (server-side regex when semantics isn't enough)

**Meta** — `xmp4_guide` (prescribed workflow — **always call this first** in a new agent session), `xmp4_server` (version + stats)

Full parameters, pagination rules, and language-specific behavior are in [`docs/tool-reference.md`](docs/tool-reference.md).

## Language coverage

**Tier 1** (primary, full coverage contract): C#, TypeScript, Python, Java, Rust, PHP.
**Tier 2** (best-effort): Go, JavaScript, Dart, Ruby, C++.

Per-language indexer quirks (e.g. empty `hierarchy.base` for TS/Rust/Java/PHP, Python `usages` cross-module under-counting) are documented honestly in [`docs/tiers-and-quirks.md`](docs/tiers-and-quirks.md). We'd rather be exact about limits than over-promise.

## Coverage growth — by demand, not speculation

The index currently holds 547 repositories / 9 145 SCIP-indexed projects. We add new libraries based on **aggregate query logs** (symbol names + repo filters, no PII, no user code) — if many AI agents search for `flask/Flask` and we don't have it, we add it. Drop a [repo-request](.github/ISSUE_TEMPLATE/request-repo.yml) to jump the queue.

## Privacy — short version

- We log **aggregate queries** (symbol names, project filters, tool names) to grow the index based on demand.
- We do **not** log the contents of your codebase. We are read-only on OSS libraries we've indexed; we never receive your project's files.
- We do **not** log personal identifiers or accounts.
- An open-aggregate-stats endpoint is planned (`/stats/top-missing`) for transparency.

Full detail in [`docs/privacy.md`](docs/privacy.md).

## Status

- Server live at `mcp.example4.ai` — v1.1.3, 547 repos, 9 145 projects, 17 MCP tools, 10 languages
- Registry submissions — in progress
- Public benchmark (token savings vs grep vs GitMCP) — in progress, fresh numbers coming before launch announcement
- Demand-driven index growth — in progress

## Ask for a library

[Open a repo-request issue](../../issues/new?template=request-repo.yml) — list the GitHub URL, the language, and one query you'd want to run. We use a combined score of user requests + aggregate query volume to prioritize.

## License

Apache 2.0 for this documentation repository. See [LICENSE](LICENSE).
The xmp4 server source is private. The hosted endpoint is free for personal and commercial use subject to the Terms of Service (TBD link).

## Issues & contact

- GitHub issues on this repo for bug reports, feature requests, or repo requests
- MCP server source (private) for commercial licensing inquiries: see repository owner profile

---

_Part of the [LSAI protocol](https://github.com/LadislavSopko/lsai-protocol) family — the open spec for semantic code intelligence in AI agents._
