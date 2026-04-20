# xmp4 Tool Reference

17 MCP tools. All examples below are **verified live** against `mcp.example4.ai` v1.1.3 on 2026-04-20. The outputs are copied verbatim from the server.

If you are writing an agent that uses xmp4 for the first time, the agent's first call should be `xmp4_guide` — that returns the authoritative, release-current workflow. This document is for humans.

---

## The prescribed workflow

xmp4 is **not** a single-call grep. It is a semantic graph navigated in a prescribed order. Skip a step and you'll see the tool misbehave — not because it's broken, but because you called it wrong.

```
  xmp4_projects  →  xmp4_search  →  xmp4_info / xmp4_source / xmp4_usages / …
  (find repo)      (get file_path)    (exact operations with file_path)
```

Three non-negotiable rules:

1. **Always pass `file_path`** on tools that accept it. Without `file_path` the tool picks the first match across the repo — often wrong when a name is shared across modules.
2. **`xmp4_search` is substring-match sorted by position-in-file.** If you know the exact name and want the canonical definition, use `xmp4_info`, not `xmp4_search`.
3. **Call-graph tools (`callers`, `callees`, `tests_for`) take method names**, not class names. Asking callers of a class returns at most instantiation sites.

---

## Core discovery

### `xmp4_projects` — find an indexed library

Parameters: `language?`, `query?`, `repo?`, `page`, `page_size`.

```
xmp4_projects(language="Python", query="flask")
→
3 project(s) found (page 1/1):
  1. flask/Flask (Python) — 4229 symbols
  2. genkit/flask-hello (Python) — 10667 symbols
  3. genkit/genkit-plugin-flask (Python) — 10667 symbols
```

Copy the identifier (`flask/Flask`) into every subsequent call's `project` parameter.

### `xmp4_search` — substring search within a project

Parameters: `project`, `query`, `kind?`, `max_results?` (default 50), `page`, `page_size`, `output_format?`.

```
xmp4_search(project="flask/Flask", query="Flask", max_results=10)
→
10 results found (page 1/1)
src/flask/sansio/app.py:40 Member FlaskCliRunner
src/flask/testing.py:265 Type FlaskCliRunner
tests/test_testing.py:12 Member FlaskCliRunner
tests/test_views.py:4 Member flask.views
tests/test_cli.py:366 Method test_flaskgroup_debug
tests/test_templating.py:325 Type MyFlask
tests/test_helpers.py:200 Type MyFlask
tests/test_subclassing.py:7 Type SuppressedFlask
src/flask/cli.py:531 Type FlaskGroup
tests/test_cli.py:22 Member FlaskGroup
```

Note what search is: every symbol whose display name **contains** `Flask`, sorted by position in file. The canonical `class Flask` is not in this top-10 page — it's found via `xmp4_info` below. Use search for discovery ("what exists"), use info for resolution ("where exactly is this known symbol").

Kind values per language are in [`tiers-and-quirks.md`](tiers-and-quirks.md).

### `xmp4_info` — canonical symbol resolution

Parameters: `project`, `symbol_name`, `file_path?`, `docs?` (`none|summary|full`), `output_format?`.

```
xmp4_info(project="flask/Flask", symbol_name="Flask", file_path="src/flask/app.py")
→
Type Flask src/flask/app.py:81
[docs available: call with docs=summary|full]
```

`xmp4_info` uses kind-priority resolution (`Class/Type/Struct/Enum > Method > Field > Symbol`) so it's the reliable fast-path when the name is known. Pair with `file_path` to disambiguate when the same name exists in multiple files.

With `docs="summary"` it returns the first paragraph of any attached doc-comment block.

### `xmp4_outline` — all symbols in a file

Parameters: `project`, `file_path`, `page`, `page_size`, `output_format?`.

```
xmp4_outline(project="flask/Flask", file_path="src/flask/app.py", page_size=10)
→
104 symbols found (page 1/11)
Member annotations :1
Member cabc :4
Member os :4
…
```

Pagination: 104 symbols across 11 pages at `page_size=10`. The guide calls outline the **most reliable tool** when you're unsure about a file — start here, drill into what you need with the others.

---

## Reading code

### `xmp4_source` — extract the body of a symbol

Parameters: `project`, `symbol_name`, `file_path?`.

Returns the raw source of exactly the method/function/type — not the entire file. On large service classes with 20+ methods, this is a 10–50× size saving over reading the whole file.

Caveat: `xmp4_source` needs a materialized source tree on the server volume. If you see `invalid_param: source base path does not exist`, the SCIP index is published but the source copy was GC'd — use `xmp4_info` + `xmp4_outline` which read SCIP metadata directly.

### `xmp4_view` — raw file excerpt by line range

Parameters: `project`, `file_path`, `from_line`, `to_line` (cap 500 lines per call).

Sometimes the SCIP extent of a symbol is off or you want surrounding context. `xmp4_view` reads the raw file bytes. Cap: 500 lines per call to avoid massive outputs; paginate by shifting `from_line`.

---

## Call graph

### `xmp4_callers` — who calls this method

Parameters: `project`, `symbol_name`, `file_path?`, `depth?` (1 = default, up to 5 for transitive BFS), `page`, `page_size`, `output_format?`.

```
xmp4_callers(project="tokio/tokio",
             symbol_name="poll",
             file_path="tokio/src/runtime/task/join.rs",
             page_size=5)
→
92 callers found (page 1/19)
can_spawn_not_send_future tokio-util/tests/spawn_pinned.rs:11
can_spawn_multiple_futures tokio-util/tests/spawn_pinned.rs:55
task_panic_propagates tokio-util/tests/spawn_pinned.rs:75
callback_panic_does_not_kill_worker tokio-util/tests/spawn_pinned.rs:100
tasks_are_balanced tokio-util/tests/spawn_pinned.rs:163
```

One call, 92 real call-sites on a method deep inside Tokio. Doing this with grep requires you to find the method definition, then grep for `.poll(` across the workspace, then filter for type-compatible hits — 3 rounds minimum, many false positives.

**Method name, not class name.** `xmp4_callers(symbol_name="Flask")` does not return method calls; pass `Flask.run` or `wsgi_app` etc.

### `xmp4_callees` — what does this method call

Same parameters as `callers`. Returns the methods/functions called from within the body of `symbol_name`.

### `xmp4_tests_for` — which tests exercise a symbol

Parameters: `project`, `symbol_name`, `file_path?`, `depth?`, `page`, `page_size`.

Combines a callers BFS with a test-file pattern filter (`tests/`, `test_*.py`, `*Test.java`, etc.) to return the subset of callers that are test code. Useful for impact analysis: "if I change this method, which tests might break?"

---

## Relationships

### `xmp4_hierarchy` — inheritance chain

Parameters: `project`, `symbol_name`, `file_path?`, `page`, `page_size`, `output_format?`.

```
xmp4_hierarchy(project="efcore/EFCore",
               symbol_name="DbContext",
               file_path="src/EFCore/DbContext.cs",
               page_size=5)
→
1176 derived types found (page 1/236)
DbContext Type base=[IInfrastructure,IDbContextDependencies,IDbSetCache,IDbContextPoolable,IResettableService]
          derived=[MultipleContext1,MultipleContext2,MultipleProvidersContext,BlogContext,ExternalProviderContext]
```

**One call** gives you the full base-interface set and the first page of 1 176 derived types. Impossible with grep at any cost — requires compiler-level type resolution.

Caveat: `base` is populated reliably for **C#** and **Dart**. For TypeScript, Rust, Java, PHP it is empty due to upstream SCIP indexer limitations. See [`tiers-and-quirks.md`](tiers-and-quirks.md#xmp4_hierarchybase-empty-for-tsrustjavaphp).

### `xmp4_usages` — every reference to a symbol

Parameters: `project`, `symbol_name`, `file_path?`, `page`, `page_size`, `output_format?`.

```
xmp4_usages(project="flask/Flask", symbol_name="Flask",
            file_path="src/flask/app.py", page_size=5)
→
165 usages found (page 1/33)
src/flask/sessions.py:150,171,175,187,195
```

Compact format groups multiple references on the same line per file, with comma-joined line numbers. Use `output_format="verbose"` to get per-occurrence detail.

Python caveat: cross-module references can be under-counted by upstream `scip-python`. In-file refs are reliable. If you need "all callers" on a Python project, `xmp4_callers` is more trustworthy than `xmp4_usages` filtered to call-sites.

### `xmp4_deps` — external dependencies

Parameters: `project`, `page`, `page_size`.

```
xmp4_deps(project="flask/Flask", page_size=10)
→
75 deps found (page 1/8)
functools . (python)
greenlet . (python)
ssl . (python)
importlib . (python)
site_app . (python)
collections . (python)
werkzeug . (python)
flask . (python)
os . (python)
jinja2 . (python)
```

Ecosystem-specific shape: `(python)` = pip/PyPI, `(npm)` for Node, `(cargo)` for Rust, `(maven)` for Java, `(nuget)` for .NET, `(composer)` for PHP. Maven/NuGet tags can be sparse due to upstream indexer behavior.

---

## Position-centric

### `xmp4_symbol_at` — resolve a symbol at file:line:column

Parameters: `project`, `file_path`, `line`, `column`.

LSP-style position lookup: given a cursor position, return the symbol whose identifier starts (or is enclosed) there. Useful in workflows where an agent is reading a file and encounters a token it wants to drill into without typing the full name.

### `xmp4_grep` — server-side regex on project source

Parameters: `project`, `pattern`, `file_glob?`, `case_sensitive?`, `max_results?`, `page`, `page_size`.

When semantics don't help (string literals, comments, config), a regex search over the project's source tree, run server-side. Returns file:line matches. This is the honest acknowledgment that some queries really are textual — xmp4 handles them in-band rather than forcing a client-side fallback.

---

## Meta

### `xmp4_guide`

No parameters. Returns the authoritative workflow document and the 17-tool reference for the **current server version**. **Every agent session should call this first** — it's the contract for what "correct use" of xmp4 means at this moment. If this document ever disagrees with `xmp4_guide`, trust the guide.

### `xmp4_server`

No parameters. Returns `xmp4 <version> (<sha>)` plus `repos_unique`, `projects_total`, `status`. Use it as a ping and to log which server version answered your benchmark.

### `xmp4_repos` (deprecated)

Removed in v0.6.0. Use `xmp4_projects` (same data source, more expressive).

---

## Errors

Every tool surfaces the same four variants:

| Variant | When |
|---|---|
| `invalid_param` | malformed `page` / `page_size` / other argument, or — on `xmp4_source` — source tree not materialized |
| `invalid_kind` | `kind` filter is not a valid SCIP kind (message lists the valid values) |
| `symbol_not_found` | the symbol name does not resolve — check dotted-name limits in [`tiers-and-quirks.md`](tiers-and-quirks.md#dotted-name-resolver--three-documented-gotchas) |
| `repo_not_found` | project identifier not in the index (quickly check with `xmp4_projects(query=…)`) |

An empty-result header like `0 results found (page 1/1)` followed by `No results.` is **not an error** — it's a normal zero-hit response. Don't pattern-match on the `No results.` string; pattern-match on the `N ... found` header line's `N=0`.

---

## Pagination and output format

- Every list-returning tool: `page` (1-based, default 1) and `page_size` (default 20, max 100).
- `xmp4_search` additionally has `max_results` (default 50) — an absolute ceiling on candidates collected from the full SCIP index; raise it to scan deeper.
- `output_format`: `"compact"` (default — examples above) or `"verbose"` (richer, adds docs and per-entry detail). Only `search`, `usages`, `outline`, `callers`, `hierarchy`, `info` respect it; `source`, `view`, `deps`, `grep` have fixed output shape.

---

## Tool summary table

| Tool | Purpose | Paginated |
|---|---|:-:|
| `xmp4_projects` | Find project by language/name | ✓ |
| `xmp4_search` | Substring search within project | ✓ |
| `xmp4_info` | Canonical symbol resolution | — |
| `xmp4_outline` | All symbols in a file | ✓ |
| `xmp4_source` | Extract symbol body | — |
| `xmp4_view` | Raw file excerpt by line range | — |
| `xmp4_callers` | Who calls this method (optional transitive BFS) | ✓ |
| `xmp4_callees` | What does this method call | ✓ |
| `xmp4_tests_for` | Callers intersect test-file patterns | ✓ |
| `xmp4_hierarchy` | Base + derived types (C#/Dart populated) | derived only |
| `xmp4_usages` | Every reference to a symbol | ✓ |
| `xmp4_deps` | External dependencies | ✓ |
| `xmp4_symbol_at` | Position-to-symbol (LSP-style) | — |
| `xmp4_grep` | Server-side regex on source | ✓ |
| `xmp4_guide` | This guide, release-current | — |
| `xmp4_server` | Version + stats | — |
| `xmp4_repos` | DEPRECATED — use `xmp4_projects` | — |

---

_Everything in this reference is kept in sync with the running server; if a tool's live output stops matching an example here, it is a **documentation bug** — [file an issue](../.github/ISSUE_TEMPLATE/bug.yml)._
