# Language tiers & indexer quirks

xmp4's guarantees are not uniform across languages. We are explicit about the difference because it matters for your AI-agent workflow.

This document is the public-facing version of the tier matrix and known limitations documented inside `xmp4_guide` (which your agent can call at any time). Everything here is **honest about what doesn't work**, on purpose — we'd rather set expectations correctly than have a reviewer find a gap and conclude the tool is broken.

---

## Tier 1 — primary, full-coverage contract

| Language | `xmp4_source` body | `xmp4_callers` | `xmp4_hierarchy.base` | `xmp4_deps` shape |
|---|---|---|---|---|
| **Python** | Full body | Reliable | Populated | `name version (pip)` |
| **TypeScript** | Full body | Reliable | **Empty** (see below) | `name version (npm)` |
| **Rust** | Full body | Reliable | **Empty** | `name version (cargo)` |
| **Java** | Mostly full; some methods fall back when SCIP `enclosing_range` is absent | Reliable | **Empty** | Sparse `. . (maven)` |
| **C#** | Full body via next-definition heuristic; rare truncation | Reliable | **Populated (when present)** | Sparse `. . (nuget)` |
| **PHP** | Bounded snippet | Reliable | **Empty** | `name version (composer)` |

## Tier 2 — best-effort

These languages are indexed but the underlying SCIP tools have known gaps we surface rather than hide.

- **Go** — scip-go emits `Type`/`Method` kinds but often falls back to `Symbol` when type inference fails. Per-package strategy was tried and reverted (it generated thousands of tiny SCIP files that killed cross-reference). Current status: re-evaluating a monorepo-style strategy.
- **JavaScript** — scip-node has display-name quirks (quoted names like `'animate.leave'`) and may report `Symbol` instead of the more specific kind. Useful for search + usages, less for hierarchy.
- **Dart** — indexer works, but the Flutter SDK must be bundled in the indexer container (we do). Class/Method kinds emitted reliably.
- **Ruby** — scip-ruby emits synthetic callee names in certain call graphs. Usages + search + outline reliable.
- **C++** — scip-clang struggles on very large projects or unusual CMake layouts. `xmp4_deps` is frequently empty.

## Class-like kinds per language

When you pass `kind` to `xmp4_search`, the valid value depends on the language. SCIP doesn't normalize these.

| Language | Class-like kind | Method/function kind |
|---|---|---|
| C# | `Type` | `Method` |
| TypeScript | `Type` (interface), `Class` | `Method`, `Function` |
| Python | `Type` (class) | `Method`, `Function` |
| Java | `Class`, `Interface` | `Method` |
| Rust | `Struct`, `Trait`, `Enum` | `Function`, `Method` |
| PHP | `Type` (class) | `Method`, `Function` |

Filter-free search (no `kind` argument) returns everything; this is often the right default.

## Known limitations (honest list)

These are **documented in `xmp4_guide`** and your agent can re-read them at any time.

### `xmp4_search` is substring-match, not exactness-first

Searching `"QuerySet"` on `django/Django` returns every `Type` whose display name contains "QuerySet" — including test classes (`QuerySetSetOperationTests`, `EmptyQuerySet`, `RawQuerySet`, etc.) — sorted by position in file, not by how closely the name matches your query. The canonical `Type QuerySet` at `django/db/models/query.py:283` is present in the result set but may not be on top.

**When the name is known exactly**, prefer `xmp4_info(project, symbol_name, file_path)` — kind-priority resolution (`Class/Type/Struct > Method > Field`) makes it reliable for the known-name fast path.

### Dotted-name resolver — three documented gotchas

`xmp4_info`, `xmp4_usages`, `xmp4_callers`, `xmp4_callees`, `xmp4_source`, `xmp4_hierarchy` accept dotted names like `Parent.method`. Three cases don't currently work as-is:

- **C# explicit interface implementations** — a method declared `void IDisposable.Dispose()` has display name `System.IDisposable.Dispose`, not `Dispose`. Asking `MyClass.Dispose` returns `symbol_not_found`. **Workaround**: search/info for the qualified name directly.
- **Multi-level nesting (3+ segments)** — `Outer.Inner.method` fails because the resolver matches parent-descriptor against SCIP's `Outer#Inner#` form, which doesn't accept a literal `Outer.Inner`. **Workaround**: use 2-segment form `Inner.method` and disambiguate with `file_path`.
- **Inherited members** — `Flask.logger` returns `symbol_not_found` because `logger` is defined on base class `App`. **Workaround**: query `App.logger` directly, or call `xmp4_hierarchy(Flask)` first to discover bases.

### `xmp4_callers` / `xmp4_callees` need method names

Passing a class name ("give me callers of `Flask`") does **not** give you call-graph entries — it gives you class instantiation sites if anything. Call-graph operations operate on **functions and methods**. Use the method name, optionally dotted (`Flask.run`).

### Python `xmp4_usages` under-counts cross-module refs

Upstream `scip-python` behavior: cross-module references can be missed. In-file references are reliable. For "all callers of this function across a repository", `xmp4_callers` is more trustworthy than `xmp4_usages` on Python — and cross-language comparisons should prefer Python's in-file counts.

### `xmp4_source` depends on a materialized source tree

The `xmp4_source` tool reads actual file bytes from a per-project disk path on our server. If the SCIP index is published but the source tree has not (or has been GC'd), you get:

```
Error: invalid_param: source base path does not exist: <path>
```

This is server-side data-pipeline state, not a client bug. `xmp4_info`, `xmp4_outline`, `xmp4_search`, and `xmp4_callers` still work because they read only SCIP metadata.

### `xmp4_hierarchy.base` empty for TS/Rust/Java/PHP

The SCIP indexers for these languages do not currently emit the base-class relationship in a form our server can walk. We surface this as an empty `base` array rather than fake data. C# and Dart have populated `base` arrays where the relationship exists in the source.

### Annotation types show as `Interface` (JVM)

Java annotations (`@ConditionalOnProperty`, etc.) are `public @interface` at the JVM level, so SCIP records them with `kind: Interface`. A search filtered by `kind=Class` will miss them. Omit the filter to match both, or search for `kind=Interface`.

---

## Pagination and output format

All list-returning tools accept `page` (1-based, default 1) and `page_size` (default 20, max 100). Every response starts with:

```
N item(s) found (page X/Y)
```

Including the empty case (`0 results found (page 1/1)` followed by `No results.`). Do not match output to a literal "No results." string — the header line is always present first.

`output_format` is `"compact"` by default (what you see above). `"verbose"` adds documentation and richer per-entry detail on `xmp4_search`, `xmp4_usages`, `xmp4_outline`, `xmp4_callers`, `xmp4_hierarchy`, `xmp4_info`. `xmp4_source` and `xmp4_deps` ignore this parameter (fixed shape).

---

## Staying current

Every release of xmp4 updates the in-tool `xmp4_guide`. If something in this document conflicts with what the tool returns **today**, trust `xmp4_guide` and file an issue pointing us at the outdated section of this file. Our AI-agent docs are meant to follow the tool, not lead it.
