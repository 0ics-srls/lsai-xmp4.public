---
name: xmp4
description: Semantic code intelligence for third-party libraries via the xmp4 MCP server (SCIP-backed, covers CSharp, TypeScript, Python, Java, Rust, PHP, Go, JavaScript, Dart, Ruby, C++). Use this skill whenever the user asks to explore, navigate, or understand an OSS or third-party library — find how an API is actually used, trace callers/callees, look up a method signature, read the real source of a class, find tests that exercise a specific symbol, or walk a type hierarchy. Trigger on phrases like "how do I use ConnectionMultiplexer.Connect in StackExchange.Redis", "show me tests for Flask.route", "find callers of UseAuthentication", "what does requests.Session.send do", "walk the hierarchy of SpringApplication", "give me examples of AmazonS3Client.PutObject". Also trigger when the user mentions xmp4 tools by name (xmp4_projects, xmp4_search, xmp4_info, xmp4_source, xmp4_usages, xmp4_callers, xmp4_callees, xmp4_outline, xmp4_hierarchy, xmp4_tests_for, xmp4_view, xmp4_grep, xmp4_deps, xmp4_symbol_at, xmp4_server, xmp4_guide). Do not trigger for questions about code the user is actively editing in their own repository, for generic language syntax questions, or when a local LSP/IDE is the more natural tool — xmp4 is for third-party, pre-indexed library exploration.
---

# xmp4 — Code Intelligence for Third-Party Libraries

xmp4 is an MCP server that answers semantic code questions over pre-indexed
OSS libraries. Reach for it **first** when the user wants to understand how
an unfamiliar library is actually used in practice — it is far cheaper and
more focused than grepping source archives or reading READMEs.

The primary value is this: instead of guessing from signatures or docs, you
can instantly find the real tests and call sites that exercise a symbol,
then read them. That is where idiomatic usage patterns actually live.

## Golden path — follow this

Whenever a user question can be answered by reading a library's source,
tests, or call graph, run this 5-step flow. It is the fastest and cheapest
route, and it is what xmp4 is designed around:

```
1. xmp4_projects(language=?, query=?)      # discover the project id
2. xmp4_search(project, query)             # find the symbol + file_path
3. xmp4_info(project, symbol_name, file_path, docs="summary")
4. xmp4_tests_for(project, symbol_name, file_path)
   → xmp4_view(project, file_path=<test file>, from_line=N, to_line=N+80)
5. If you need more context: xmp4_usages / xmp4_callers / xmp4_outline
```

Step 4 is the killer feature. `xmp4_tests_for` filters SCIP callers by
per-language test-file patterns (e.g. `*Tests.cs`, `test_*.py`,
`*.spec.ts`) and typically returns 3–20 real tests — you then `xmp4_view`
the interesting ones to see concrete usage.

## The rules that actually matter

These are the rules that change whether you get an answer in 2 calls vs. 10.

**1. Always pass `file_path`.** On info/source/usages/callers/callees/
tests_for/hierarchy, omitting `file_path` forces a cross-file
disambiguation walk that is roughly 80× slower (~4 ms → ~300 ms). Get
the path from `xmp4_search` and carry it through every follow-up call.
Many symbols share names — without `file_path` the resolver picks the
first match, which is often wrong.

**2. Method names for callers/callees, not class names.** Callers and
callees operate on functions and methods. Asking for callers of `Flask`
(a class) gives instantiation sites, not method calls on instances. If
you want to know who invokes a class's methods, resolve a specific
method first.

**3. Search first, copy exactly.** `xmp4_search` returns the canonical
`display_name` and `file_path`. Copy those verbatim into subsequent
calls — do not guess. If a search returns nothing, try a shorter
substring; the search is case-insensitive substring match, ranked by
position-in-file rather than exactness, so partial matches are fine for
discovery.

**4. `xmp4_outline` is the most reliable first look.** When you do not
know a file's structure, outline it. You will see every symbol with its
kind and line — the quickest way to orient yourself before drilling
deeper.

**5. Prefer view over source.** When you already know the line range,
`xmp4_view(project, file_path, from_line, to_line)` reads the raw file
directly — fast and cheap. Use `xmp4_source` only when you want the
SCIP next-def heuristic to carve out a specific symbol body, and keep
in mind that it occasionally truncates on CSharp/Java. If `xmp4_source`
returns a body that starts mid-statement or is unexpectedly short,
switch to `xmp4_view` with `from_line` taken from the `xmp4_search`
result.

## Cost budget — preserve the shared server

The xmp4 server is shared with many clients and RAM is the bottleneck.
Knowing which tools are cheap and which are expensive keeps it healthy
and keeps your requests fast.

**Cheap — free to use at will.** Everything SCIP-backed reads in-memory
metadata loaded at startup; a query is a hash/tree lookup in
microseconds with no transient allocations. This covers: `xmp4_projects`,
`xmp4_search`, `xmp4_info`, `xmp4_usages`, `xmp4_callers`, `xmp4_callees`,
`xmp4_tests_for`, `xmp4_outline`, `xmp4_hierarchy`, `xmp4_symbol_at`,
`xmp4_deps`, `xmp4_server`, `xmp4_guide`.

**Moderate — bounded I/O.** `xmp4_view` reads a bounded line range from
disk (hard cap 500 lines per call). `xmp4_source` is slightly heavier
because it walks SCIP ranges to compute the body. Keep view ranges
tight (40–80 lines) unless there is a specific reason to grab more.

**Heavy — do not use by default.** `xmp4_grep` runs ripgrep internals.
Even in single-file mode it is 2–3× more expensive than a SCIP lookup;
in multi-file walk mode it is ~200× more expensive and mmap-heavy.

## Grep policy — single file, last resort

`xmp4_grep` has two tiers:

- **Free tier.** `file_path` (single file, repo-relative) is required.
  Every call scopes to exactly one file.
- **Premium tier.** Multi-file walks via `file_glob` are available only
  when the server is configured with `XMP4_PREMIUM_GREP_WALK=true`.
  Requesting `file_glob` without premium returns an explicit error.

Use grep **only** for text that is provably not a SCIP symbol: config
keys, URL or connection-string literals, environment variable names in
code, macro-generated identifiers absent from the index, comments, or
docstring content.

**Never use grep to find tests that use a method** — `xmp4_tests_for` is
the cheap, SCIP-backed way to get that list. Likewise never grep to find
callers or usages — those have dedicated SCIP tools that are far
cheaper and return structured results.

Never grep in a loop. One targeted single-file call, then navigate with
`xmp4_view`. If you find yourself wanting to grep across many files,
that is almost always a sign that a SCIP tool (`xmp4_search`,
`xmp4_tests_for`, `xmp4_usages`) is the right answer.

## Language kind matrix

The `kind` field in `xmp4_search` results is what the SCIP indexer
assigned for the target language. The tier-1 languages have dependable,
consistent kind tagging:

| Language   | Class-like kind             | Method/function kind    |
|------------|-----------------------------|-------------------------|
| CSharp     | Type                        | Method                  |
| TypeScript | Type (interface), Class     | Method, Function        |
| Python     | Type (class)                | Method, Function        |
| Java       | Class, Interface            | Method                  |
| Rust       | Struct, Trait, Enum         | Function, Method        |
| PHP        | Type (class)                | Method, Function        |

Tier-2 quick notes: Go emits Type/Method (often Symbol when scip-go
cannot infer); JavaScript emits Symbol with scip-node quirks (quoted
`display_name` like `'animate.leave'`); C++ mixes Symbol entries; Dart
emits Class/Method. When you filter with `xmp4_search(kind=...)`, pick
the kind from the row above.

## Dotted-name resolution and its limits

You can pass `Parent.method` to `xmp4_info`, `xmp4_usages`,
`xmp4_callers`, `xmp4_callees`, `xmp4_source`, `xmp4_hierarchy`,
`xmp4_tests_for`. The resolver splits on the rightmost `.`, looks up
`method` in the name index, and filters candidates whose `symbol_id`
contains `Parent` as a descriptor segment.

Three known limitations to recognize — if you hit one of these, do not
keep retrying the same query, switch approach:

- **CSharp explicit interface implementations.** Methods declared as
  `void IDisposable.Dispose()` have `display_name`
  `System.IDisposable.Dispose`, not `Dispose`. Asking `MyClass.Dispose`
  may return `symbol_not_found`. Workaround: search and call the
  qualified name (`System.IDisposable.Dispose`) directly.
- **Multi-level nesting (3+ segments)** currently fails because the
  matcher checks literal `Outer.Inner` against SCIP's `Outer#Inner#`
  form. Workaround: use `Inner.method` (2 segments) and disambiguate
  with `file_path`.
- **Inherited members are not walked.** `Flask.logger` returns
  `symbol_not_found` because `logger` is defined on base class `App`.
  Workaround: query `App.logger` directly, or use
  `xmp4_hierarchy(Flask)` to discover bases first.

## Indexer quality matrix (tier-1)

| Language   | xmp4_source body                                               | xmp4_callers | xmp4_hierarchy.base | xmp4_deps                 |
|------------|----------------------------------------------------------------|--------------|---------------------|---------------------------|
| Python     | Full body                                                      | Reliable     | Yes                 | `name version (pip)`      |
| TypeScript | Full body                                                      | Reliable     | Empty               | `name version (npm)`      |
| Rust       | Full body                                                      | Reliable     | Empty               | `name version (cargo)`    |
| Java       | Mostly full; some methods fall back when SCIP enclosing_range is absent | Reliable | Empty               | Sparse `. . (maven)`      |
| CSharp     | Full body via next-def heuristic; rare cases truncate          | Reliable     | Yes (when present)  | Sparse `. . (nuget)`      |
| PHP        | Bounded                                                        | Reliable     | Empty               | `name version (composer)` |

If `xmp4_source` returns a body that looks truncated or starts mid-
statement, jump immediately to `xmp4_view(project, file_path,
from_line=<line from xmp4_search>, to_line=from_line+80)`. Do not
iterate `xmp4_source` with different symbol names hoping to get a
cleaner cut — the next-def boundary is what it is.

## Pagination

Every list-returning tool accepts:

- `page` (1-based, default 1). `page=0` returns `invalid page (1-based)`.
- `page_size` (default 20, max 100). `0` or `>100` returns an error.

Every response begins with a header line — including empty results (do
not compare output against the literal `No results.`):

```
N <item>(s) found (page X/Y)
```

For 0 hits the line is `0 results found (page 1/1)` (or `0 match(es)`,
`0 dep(s)`, etc., with the per-tool noun) followed by `No results.`.

### `max_results` vs `page_size`

- `max_results` (xmp4_search only, default 50) is an absolute ceiling on
  candidates collected from the full SCIP index.
- `page_size` (default 20, max 100) paginates within that ceiling.

To scan beyond the first 50 hits for a substring-heavy query, raise
`max_results` first, then page through.

## `docs` parameter on `xmp4_info`

- `docs="none"` (default): header only; if docs exist, appends
  `[docs available: call with docs=summary|full]`.
- `docs="summary"`: first paragraph of each doc block.
- `docs="full"`: every doc block, unbounded.

## `output_format`

Accepts `"compact"` (default) or `"verbose"`. Verbose adds documentation
lines and richer per-entry detail. `xmp4_source` and `xmp4_deps` ignore
this parameter (their output shape is fixed).

## When source reads return `source base path does not exist`

`xmp4_source` and `xmp4_view` read actual file content from a
per-project `SourceBasePath` on the server data volume. The other tools
(info, outline, search, callers, usages, hierarchy) still work without
source on disk — they read SCIP metadata only.

If you see:

```
Error: invalid_param: source base path does not exist: <path>
```

the index was published but the source tree is not materialized yet.
That is a server-side data-pipeline state, not a client mistake. Use
info/outline/search/callers/usages for that project until source is
re-materialized; do not retry `xmp4_source` hoping for a different
answer.

## Tool reference

| Tool             | Purpose                                                | Cost     | Paginated    |
|------------------|--------------------------------------------------------|----------|--------------|
| xmp4_projects    | Find project by name/language                          | cheap    | yes          |
| xmp4_search      | Find symbols by name                                   | cheap    | yes          |
| xmp4_info        | Symbol details + docs                                  | cheap    | no           |
| xmp4_usages      | All references to a symbol                             | cheap    | yes          |
| xmp4_callers     | Who calls this method (optional `depth=1..=5`)         | cheap    | yes          |
| xmp4_callees     | What this method calls (optional `depth=1..=5`)        | cheap    | yes          |
| xmp4_outline     | All symbols in a file                                  | cheap    | yes          |
| xmp4_hierarchy   | Inheritance chain (derived list paginates)             | cheap    | derived only |
| xmp4_source      | Extract symbol source (SCIP next-def heuristic)        | moderate | no           |
| xmp4_view        | Raw file excerpt by line range (cap 500 lines)         | moderate | no           |
| xmp4_grep        | Text search. Free: `file_path` required. Premium: multi-file walk via `file_glob`. | heavy    | yes          |
| xmp4_symbol_at   | Position→symbol lookup (LSP-style)                     | cheap    | no           |
| xmp4_tests_for   | Tests exercising a symbol (callers × test-file pattern)| cheap    | yes          |
| xmp4_deps        | External dependencies                                  | cheap    | yes          |
| xmp4_server      | Server version + stats                                 | cheap    | no           |
| xmp4_guide       | Skill pointer + minimal cheatsheet                     | cheap    | no           |

## Error variants

- `invalid_param`: malformed `page`/`page_size`/other, missing source
  base path, missing `file_path` in free-tier grep, path traversal in
  `file_path` (rejected: absolute paths and `..` segments),
  `file_glob` without premium tier.
- `invalid_kind`: unknown SCIP kind filter; message lists valid values.
- `symbol_not_found`: no candidate resolved for the symbol name.
- `repo_not_found`: project identifier not in the index.

## Common mistakes — watch for these

- **Grepping as a default search.** Grep is the slowest tool. Whenever
  the target is a SCIP symbol, prefer `xmp4_search` / `xmp4_tests_for` /
  `xmp4_usages`. Grep is for text that is NOT indexed.
- **Omitting `file_path`** on info/usages/callers/source/tests_for/
  hierarchy. The resolver fast-path is ~80× faster when `file_path` is
  supplied.
- **Calling `xmp4_callers("ClassName")`** instead of a method name.
  Callers/callees work on functions and methods.
- **Treating `0 results found (page 1/1)` as an error string.** It is
  the normal empty-result header.
- **Asking `MyClass.Method`** for an inherited member or explicit
  interface impl — see dotted-name limitations above.
- **Relying on `xmp4_repos`** (deprecated since v0.6.0 — use
  `xmp4_projects`).
- **Grepping `tests/**` to find usage examples.** `xmp4_tests_for` is
  the SCIP-backed way; grep walks every file.

## Quick reference card

```
# Discover
xmp4_projects(language=?, query=?)

# Resolve
xmp4_search(project, query) → file_path + display_name
xmp4_info(project, symbol_name, file_path, docs="summary")

# Navigate
xmp4_outline(project, file_path)
xmp4_callers / callees / usages / hierarchy (project, symbol_name, file_path)

# Read
xmp4_source(project, symbol_name, file_path)
xmp4_view(project, file_path, from_line, to_line)

# Tests-driven exploration (primary use case)
xmp4_tests_for(project, symbol_name, file_path)
→ xmp4_view(project, <test file>, from_line, to_line+80)

# Text grep — last resort, single file only in free tier
xmp4_grep(project, pattern, file_path)
```

## Versioning and re-fetch

When `xmp4_guide` on the server reports a skill version higher than the
one you saved locally, re-fetch the skill file. The URL is stable; the
query string `?v={version}` acts as the cache key.

Authoritative source: <https://example4.ai/xmp4-skill.md>.
