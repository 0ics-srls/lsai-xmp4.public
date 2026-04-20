# Pre-Benchmark Findings — xmp4 v1.1.3 Live

**Date**: 2026-04-20 (revised after reading `xmp4_guide`) · **Environment**: `mcp.example4.ai` v1.1.3

---

## Revised understanding (this replaces an earlier incorrect draft)

`xmp4_search` is **substring-match sorted by position-in-file, by design** (documented in `xmp4_guide` under *"Search ranking — substring, not exact-first"*). It is the **discovery** tool. The canonical fast-path for a known symbol is `xmp4_info(project, symbol_name, file_path)` which uses kind-priority resolution (Class/Type/Struct/Enum > Method > Field).

The prescribed workflow (from the guide, non-negotiable for our benchmark):

1. `xmp4_projects(language=…, query=…)` → project identifier
2. `xmp4_search(project, query=…)` → pick the **file_path** + **display_name** of the intended candidate from the substring list
3. `xmp4_info | xmp4_source | xmp4_usages | xmp4_callers | …` with **both** `symbol_name` AND `file_path`

Any benchmark that skips step 2's file_path capture is measuring tool misuse, not the tool. That is now the design constraint.

## Verified results (no blocker)

All 5 target repos are indexed with expected symbol counts. Exact-name lookup via `xmp4_info` is correct in every spot check:

| Repo | Symbol | `xmp4_info` response |
|---|---|---|
| `django/Django` | QuerySet | `Type QuerySet django/db/models/query.py:283` |
| `efcore/EFCore` | DbContext | `Type DbContext src/EFCore/DbContext.cs:49` |
| `spring-boot/spring-boot` | SpringApplication | `Class SpringApplication spring-boot-project/spring-boot/src/main/java/org/springframework/boot/SpringApplication.java:188` |
| `tokio/tokio` | JoinHandle (via search pos.1) | `Struct JoinHandle tokio/src/runtime/task/join.rs:163` |
| `angular/ng-template` | LanguageService (via search) | top-5 contain the canonical type |

## Tool-reference & connect-instructions requirements

These come out of `xmp4_guide` (Critical Rules) and must be surfaced in our public docs verbatim, not invented:

1. **Always pass `file_path`** on info/source/usages/callers/callees/hierarchy when you have it. Without it the tool picks the first match, often wrong (explicit warning in the guide).
2. **Callers/callees take method names, not class names** — asking callers of a class returns instantiation sites, not method calls.
3. **Search → copy file_path → then exact calls.** This is the workflow the guide prescribes; our public examples must show it, not shortcut it.
4. **`xmp4_hierarchy` works best for CSharp and Dart** — the guide explicitly notes the base-class walk is empty for TS/Rust/Java/PHP due to SCIP indexer limits. Our Python / Java hierarchy examples must be honest about this.
5. **Dotted-name has known limits**: C# explicit interface impls (`MyClass.Dispose` when declared `void IDisposable.Dispose()`), 3+ segment nesting, and inherited members (`Flask.logger` where `logger` is on base `App`) all return `symbol_not_found` — each has a documented workaround.
6. **`xmp4_source` needs a materialized source tree** on the server volume; if missing the error is `invalid_param: source base path does not exist`. Server-side data-pipeline state, not client bug.
7. **Python `xmp4_usages` can under-count cross-module refs** — scip-python upstream behavior, not an xmp4 bug; document it honestly.
8. **Tier-1 languages (full coverage contract):** C#, TypeScript, Python, Java, Rust, PHP. **Tier-2 (best-effort):** Go, JS, Dart, Ruby, C++. This must appear in the public README so reviewers don't benchmark on Go and conclude the tool is weak.

## Benchmark implication

The fair AI-agent workflow to compare against grep is the two-step one from the guide:

- **Scenario A (known name)**: 1 call — `xmp4_info(symbol_name, file_path)`.
- **Scenario B (partial / discovery)**: 2 calls — `xmp4_search(query)` then `xmp4_info(symbol_name, file_path)` with the file_path read off the search result.

Both will be scored against grep, separately. Scenario B is the fair head-to-head vs grep's "search → filter → read" loop. Scenario A is the fair head-to-head against grep's "I know the file already, read it" loop (`cat file.py`).

## No launch blockers found

The v1 search-ranking concern was operator error on my part, not a product defect. Proceed with benchmark build-out.
