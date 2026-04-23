<div align="center">

# xmp4

### Stop grepping library source.
### Your AI gets the compiler's view of **856 OSS libraries** via MCP.

[![live](https://img.shields.io/badge/mcp.example4.ai-live%20v1.2.1-22c55e?style=flat-square)](https://mcp.example4.ai/mcp)
[![registry](https://img.shields.io/badge/Official%20MCP%20Registry-ai.example4%2Fxmp4-f59e0b?style=flat-square)](https://registry.modelcontextprotocol.io/v0/servers?search=xmp4)
[![license](https://img.shields.io/badge/license-Apache%202.0-blue?style=flat-square)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Streamable%20HTTP-f59e0b?style=flat-square)](https://modelcontextprotocol.io)
[![repos](https://img.shields.io/badge/libraries-856%20indexed-f59e0b?style=flat-square)](#language-coverage)
[![vs GitMCP](https://img.shields.io/badge/vs%20GitMCP-42%C3%97%20fewer%20tokens-f59e0b?style=flat-square)](docs/benchmarks/WHITEPAPER.md)

**Real callers. Real source. Real hierarchy. In 3 tool calls.**

[**→ Landing page**](https://example4.ai) · [**→ Benchmark whitepaper**](docs/benchmarks/WHITEPAPER.md) · [**→ Connect in 30 seconds**](docs/connect-instructions.md)

</div>

---

## The 30-second pitch

Your AI coding agent is burning tokens grepping OSS libraries it will barely use. **xmp4** is a hosted MCP server that pre-indexes 856 popular open-source libraries with **SCIP** — the semantic code format Sourcegraph uses — and serves them through 17 tools. No clone. No grep. No false positives.

```text
ASK: "Who calls Flask.wsgi_app in the flask repo and what does it do?"

with grep + local clone:
  git clone flask/flask          ~40 MB,   ~2 min
  grep -rn "wsgi_app" .          200+ matches, mostly noise
  cat src/flask/app.py | sed ... read 1000+ lines to find the body
  filter false positives         model spends tokens deciding what's real
  ──────────────────────────────────────
  total:                         ~15,000 tokens + disk + wall time

with xmp4:
  xmp4_info(symbol_name="Flask",    file_path="src/flask/app.py")         → signature,  20 tok
  xmp4_source(symbol_name="wsgi_app", file_path="src/flask/app.py")       → body,      180 tok
  xmp4_callers(symbol_name="wsgi_app", file_path="src/flask/app.py")      → 1 caller,   50 tok
  ──────────────────────────────────────
  total:                                                                    ~250 tokens

xmp4 is 60× cheaper here — and every result is SCIP-resolved, not text-matched.
```

## The measured numbers (4 big OSS libs · [reproducible](docs/benchmarks/WHITEPAPER.md))

Same realistic question on spring-boot · tokio · django · efcore: *"give me the signature, body, and real callers of X."*

| | **xmp4** | grep + clone | GitMCP | Context7 |
|---|---:|---:|---:|---:|
| Total tokens (same question) | **1 558** | 2 978 | **65 629** | — |
| vs xmp4 | 1× | 1.9× more | **42× more** | can't answer |
| Returns real source body? | ✅ | ✅ noisy | ✗ file paths only | ✗ curated docs only |
| Semantic callers? | ✅ | ✗ | ✗ | ✗ |
| Type hierarchy? | ✅ | ✗ | ✗ | ✗ |
| Setup cost | 0 | GBs of clone | 0 | 0 |

> GitMCP and Context7 look cheaper **per call** because they return less. To reach the same answer, GitMCP balloons to 42× more tokens — and still can't produce the semantic caller list. Context7 can't at any cost. [**Full whitepaper with Python harness →**](docs/benchmarks/WHITEPAPER.md)

## Connect in 30 seconds

```jsonc
// Claude Code / Cursor / Claude Desktop — project `.mcp.json` or client config
{
  "mcpServers": {
    "xmp4": {
      "type": "http",
      "url": "https://mcp.example4.ai/mcp"
    }
  }
}
```

(The ready-to-paste config also lives at [`.mcp.json`](.mcp.json) in this repo.)

### Teach Claude how to use xmp4 (optional but recommended)

Install the xmp4 skill once per version — Claude will pick the cheapest tool path automatically (tests_for + view over grep):

```bash
# Claude Code
mkdir -p ~/.claude/skills/xmp4 && \
  curl -sfL https://example4.ai/xmp4-skill.md -o ~/.claude/skills/xmp4/SKILL.md

# Other clients: just tell Claude to read the URL when using xmp4 tools
#   https://example4.ai/xmp4-skill.md
```

Restart your client. Then try (every step verified live 2026-04-24):

> *"Using xmp4, find the Flask class in `flask/Flask` and list its usages."*

You should see `Type Flask src/flask/app.py:81` and 165 usages across 33 result pages. One semantic call per question. Zero grep loops.

**Setup for Cursor · Claude Desktop · Continue · Windsurf** → [`docs/connect-instructions.md`](docs/connect-instructions.md)

## The 17 tools

[**Full reference with live examples**](docs/tool-reference.md)

**Semantic core** (where the value lives)
`xmp4_projects` · `xmp4_search` · `xmp4_info` · `xmp4_usages` · `xmp4_callers` · `xmp4_callees` · `xmp4_hierarchy` · `xmp4_outline` · `xmp4_source` · `xmp4_tests_for` · `xmp4_deps` · `xmp4_symbol_at`

**Convenience**
`xmp4_view` (raw file excerpt by line range) · `xmp4_grep` (server-side regex when semantics isn't enough)

**Meta**
`xmp4_guide` (returns a **versioned skill pointer** to `https://example4.ai/xmp4-skill.md` — fetch once per version and save as a local Claude Code skill; embeds a minimal cheatsheet as offline fallback) · `xmp4_server` (version + stats)

## Language coverage

**Tier 1** — full coverage contract
<br>`C#` · `TypeScript` · `Python` · `Java` · `Rust` · `PHP`

**Tier 2** — best-effort, documented quirks
<br>`Go` · `JavaScript` · `Dart` · `Ruby` · `C++`

Every known limitation — empty `hierarchy.base` on TS/Rust/Java/PHP, Python cross-module `usages` under-count, C# explicit-interface-impl dotted-name behaviour — is listed verbatim in [`docs/tiers-and-quirks.md`](docs/tiers-and-quirks.md). We'd rather set expectations correctly than have a reviewer find a gap and assume the whole thing is inflated.

## Coverage grows by demand, not by guesswork

The index currently holds 856 repositories / 15 921 SCIP-indexed projects. We add new libraries based on two signals, combined:

1. **Aggregate query logs** — symbol names and project filters, no PII, no user code. If many AI agents search for a library we don't have, we see it.
2. **Your request** — [file a repo-request issue](../../issues/new?template=request-repo.yml) with the GitHub URL, the language, and one concrete query you want to run. A single user request + downstream query demand almost always means **indexed within days**.

A public `/stats/top-missing` endpoint is planned — full transparency on what drives the growth loop.

## Privacy — short version

- ✓ **We log**: aggregate query counts (symbol/project/tool names, coarse timestamps) to grow the index by demand.
- ✗ **We don't log**: the contents of your codebase · personal identifiers · request bodies beyond declared tool parameters.
- Standard nginx access logs kept 7 days for abuse prevention, then purged. Not joined with query tallies.

Full detail → [`docs/privacy.md`](docs/privacy.md).

## Status

- 🟢 **Live** — `mcp.example4.ai` v1.2.1 · 856 repos · 15 921 projects · 17 tools · 11 languages
- 🟢 **Benchmark published** — [reproducible whitepaper with Python harness](docs/benchmarks/WHITEPAPER.md)
- 🟢 **Listed on the Official MCP Registry** as [`ai.example4/xmp4`](https://registry.modelcontextprotocol.io/v0/servers?search=xmp4) (DNS-authed on `example4.ai`)
- 🟢 **Smithery** — [smithery.ai/servers/0ics-srl/xmp4](https://smithery.ai/servers/0ics-srl/xmp4)
- 🟢 **Cursor Directory** — [cursor.directory/plugins/lsai-xmp4public](https://cursor.directory/plugins/lsai-xmp4public)
- 🔧 **More registry submissions in flight** — MCP.so, mcpservers.org, partnerships@github.com, awesome-lists (PRs open on punkpeye/jaw9c/appcypher)
- 🔧 **Demand-driven growth loop** — in progress

## What's in this repository

| Path | Purpose |
|---|---|
| [`docs/connect-instructions.md`](docs/connect-instructions.md) | 5 MCP clients, proof-of-life sequence, troubleshooting |
| [`docs/tool-reference.md`](docs/tool-reference.md) | 17 tools with live-verified examples and workflow rules |
| [`docs/tiers-and-quirks.md`](docs/tiers-and-quirks.md) | Language tier matrix + every known limitation, verbatim |
| [`docs/privacy.md`](docs/privacy.md) | What we log, what we don't, GDPR contact |
| [`docs/request-repo.md`](docs/request-repo.md) | How the demand-driven queue actually works |
| [`.mcp.json`](.mcp.json) | Ready-to-paste MCP client config (`type: http`, URL) |
| [`skills/xmp4/SKILL.md`](skills/xmp4/SKILL.md) | Claude Code skill — workflow, cost budget, grep policy, common mistakes |
| [`html/xmp4-skill.md`](html/xmp4-skill.md) | Same skill, served publicly at `https://example4.ai/xmp4-skill.md` |
| [`server.json`](server.json) | Official MCP Registry manifest (DNS-authed `ai.example4/xmp4`) |
| [`glama.json`](glama.json) | Glama catalog auto-index hook |
| [`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/) | Bug · feature-request · **request-repo** templates |

## Related

- [**LSAI protocol**](https://github.com/LadislavSopko/lsai-protocol) — open spec for semantic code intelligence in AI agents.
- [**SCIP**](https://github.com/sourcegraph/scip) — the semantic code format xmp4 is built on (Sourcegraph-developed, BSD-3).
- [**Model Context Protocol**](https://modelcontextprotocol.io) — the open transport spec xmp4 speaks.

## License

Apache 2.0 for this documentation repository — see [LICENSE](LICENSE).
The hosted `mcp.example4.ai` endpoint is free for personal and commercial use (TOS link pending).

Commercial licensing or self-hosted deployment enquiries → open a GitHub issue labelled `commercial` on this repo.

---

<div align="center">

Made with semantic intelligence instead of grep.

[SCIP](https://github.com/sourcegraph/scip) · [MCP](https://modelcontextprotocol.io) · [LSAI](https://github.com/LadislavSopko/lsai-protocol)

</div>
