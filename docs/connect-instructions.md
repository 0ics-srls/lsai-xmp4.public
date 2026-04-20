# Connect xmp4 to your AI coding assistant

xmp4 is an **MCP server with Streamable HTTP transport** at `https://mcp.example4.ai/mcp`. Any MCP client that speaks Streamable HTTP connects directly. Clients that only speak stdio can bridge via `mcp-remote`.

**Valid on**: 2026-04-20. MCP clients evolve fast; if your client's config schema has changed since, open an issue with the current doc link and we'll update.

---

## Claude Code (Anthropic)

Edit `~/.claude/mcp.json` (Linux/macOS) or `%USERPROFILE%\.claude\mcp.json` (Windows):

```jsonc
{
  "mcpServers": {
    "xmp4": {
      "transport": {
        "type": "http",
        "url": "https://mcp.example4.ai/mcp"
      }
    }
  }
}
```

Restart Claude Code. Verify with `/mcp` — you should see `xmp4` listed with 17 tools.

**Minimum version**: Claude Code v0.14 (Streamable HTTP transport). Earlier versions need the `mcp-remote` stdio bridge (see *Fallback* below).

**First query that proves it works**:

> *"Call xmp4_guide and then summarize what the workflow looks like."*

---

## Cursor

Cursor stores MCP config at `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` inside a project (project-scoped).

```jsonc
{
  "mcpServers": {
    "xmp4": {
      "url": "https://mcp.example4.ai/mcp"
    }
  }
}
```

Cursor auto-detects HTTP vs stdio from the presence of `url` vs `command`. Restart Cursor, open Settings → MCP, the `xmp4` entry should show 17 tools.

**One-click install**: the [Cursor Directory page](https://cursor.directory/plugins/xmp4) has an "Add to Cursor" button that writes this snippet for you. (Live once we complete directory submission — track status in the repository README.)

---

## Claude Desktop (macOS / Windows)

Claude Desktop as of April 2026 natively supports remote Streamable HTTP via `Settings → Connectors`. For xmp4:

1. Open **Claude Desktop → Settings → Connectors**.
2. Click **Add custom connector**.
3. Name: `xmp4`. URL: `https://mcp.example4.ai/mcp`. Auth: `None`.
4. Save. xmp4 appears in the connector list — toggle it on per conversation.

**If your Claude Desktop predates custom connectors** (older than v0.8), edit the legacy config file directly:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Use the `mcp-remote` stdio bridge (requires `npx`):

```jsonc
{
  "mcpServers": {
    "xmp4": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.example4.ai/mcp"]
    }
  }
}
```

Fully quit and reopen Claude Desktop.

---

## Continue (VS Code / JetBrains)

Continue's MCP config lives alongside the main config — `~/.continue/config.yaml` (preferred) or the legacy `~/.continue/config.json`.

YAML form:

```yaml
mcpServers:
  - name: xmp4
    type: streamable-http
    url: https://mcp.example4.ai/mcp
```

JSON form (legacy):

```json
{
  "mcpServers": [
    {
      "name": "xmp4",
      "type": "streamable-http",
      "url": "https://mcp.example4.ai/mcp"
    }
  ]
}
```

Reload the Continue panel in your IDE; the tool list under `xmp4` should appear.

---

## Windsurf (Codeium)

Windsurf stores MCP config at `~/.codeium/windsurf/mcp_config.json`:

```jsonc
{
  "mcpServers": {
    "xmp4": {
      "serverUrl": "https://mcp.example4.ai/mcp"
    }
  }
}
```

Restart Windsurf. Open Cascade → settings (cog icon) → MCP Servers; `xmp4` with 17 tools should appear.

---

## Fallback — `mcp-remote` stdio bridge for any stdio-only client

If your MCP client hasn't implemented Streamable HTTP yet, `mcp-remote` (an npm package maintained by geelen) translates stdio ↔ remote HTTP on the fly:

```jsonc
{
  "mcpServers": {
    "xmp4": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.example4.ai/mcp"]
    }
  }
}
```

Requires Node.js ≥ 18 on your machine. The first run downloads `mcp-remote`, subsequent runs are instant.

---

## What to try first — proof of life

Once the tool list shows 17 tools, run this exact sequence. Every step is verified live against `mcp.example4.ai` on 2026-04-20 and returns the indicated concrete result.

1. `"Call xmp4_guide."` — returns the authoritative workflow document and the 17-tool reference. Read it. If this step fails, the connection itself is broken (see troubleshooting).
2. `"Call xmp4_projects(language='Python', query='flask')."` — returns `flask/Flask (Python) — 4229 symbols` among the top results.
3. `"Call xmp4_info(project='flask/Flask', symbol_name='Flask', file_path='src/flask/app.py')."` — returns `Type Flask src/flask/app.py:81` (SCIP labels Python classes as `Type`).
4. `"Call xmp4_usages(project='flask/Flask', symbol_name='Flask', file_path='src/flask/app.py')."` — returns 165 usages across 33 pages. This one tool call would replace dozens of grep passes in a normal AI workflow — that is the point.

Want a call-graph demo? Try `xmp4_callers(project='tokio/tokio', symbol_name='poll', file_path='tokio/src/runtime/task/join.rs')` — 92 callers, one call.

If step 1 returns the guide, your client is correctly connected. If the tool list is empty in your client's UI, check: server URL is exactly `https://mcp.example4.ai/mcp` (note the trailing `/mcp`), your client supports Streamable HTTP, and your firewall allows outbound HTTPS on port 443.

---

## Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| Client shows 0 tools | URL missing trailing `/mcp` | Append `/mcp` to the URL |
| Client shows 0 tools | Client only supports stdio | Use `mcp-remote` bridge (fallback snippet above) |
| Tool call returns "source base path does not exist" | That project's source tree was not materialized server-side | Use `xmp4_info`, `xmp4_outline`, `xmp4_search` which read only SCIP metadata; or open an issue referencing the project |
| `xmp4_hierarchy` returns empty `base` for TS/Rust/Java/PHP | SCIP indexer limitation upstream | Use `xmp4_info` + manual `xmp4_search` on the parent name — documented in [`tiers-and-quirks.md`](tiers-and-quirks.md) |
| `xmp4_callers` returns nothing for a class name | Callers/callees expect **method names**, not class names | Call on the method, e.g. `Flask.run`, not `Flask` |

---

## Keeping this doc honest

If a config snippet above does not work on your client version, please [open a bug](../.github/ISSUE_TEMPLATE/bug.yml) with:
- Client name + exact version
- Snippet you used
- Error output or symptom

We verify fixes against the running server before updating this file.
