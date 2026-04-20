# 4-Backend Big-Repo Benchmark — 2026-04-20

**Backends**: xmp4 (live) · grep+clone (local) · GitMCP (hosted) · Context7 (hosted).
**Corpus**: 4 tier-1 big OSS libraries (spring-boot, tokio, django, efcore) — shallow-cloned for grep baseline, indexed on xmp4 live, queried live on `gitmcp.io` and `mcp.context7.com`.
**Task per repo**: *"Understand SYMBOL — give me its signature, the actual method body, and the real callers inside the library."*
**Tokenizer**: `tiktoken` `cl100k_base`. Identical for every backend.
**Reproducibility**: `run_bigrepo_4backend.py` in this directory — every MCP response captured verbatim.

---

## Raw tokens table

| Repo | xmp4 | grep+clone | GitMCP | Context7 | xmp4 vs grep | xmp4 vs GitMCP | xmp4 vs Context7 |
|---|---:|---:|---:|---:|---:|---:|---:|
| spring-boot | 667 | 1 039 | 287 | 323 | **1.6× less** | 2.3× more | 2.1× more |
| tokio | 409 | 685 | 150 | 164 | **1.7× less** | 2.7× more | 2.5× more |
| django | 249 | 368 | 117 | 180 | **1.5× less** | 2.1× more | 1.4× more |
| efcore | 233 | 886 | 98 | 149 | **3.8× less** | 2.4× more | 1.6× more |
| **TOTAL** | **1 558** | **2 978** | **652** | **816** | **+48 %** | **−139 %** | **−91 %** |

_xmp4 measured with pure-compact `output_format` default, no `docs` parameter — the minimum-verbosity request. Adding `docs="summary"` on `xmp4_info` adds ~5-80 tokens/call depending on how much doc-comment the symbol has (big on EFCore XML docs)._

Number of tool calls: xmp4=12, grep=12 (incl. clone), GitMCP=4, Context7=5.

## The inconvenient truth — and why it's actually xmp4's strongest point

**Raw-token arithmetic says xmp4 loses to GitMCP (2.5× more tokens) and Context7 (2× more tokens).**

This number is useless in isolation. The four backends are **not answering the same question**. A reviewer on HN who sees "GitMCP is cheaper" doesn't realize that GitMCP returned file paths and Context7 returned hello-world snippets, while xmp4 returned the actual answer to the actual task.

Fair framing: **tokens-to-complete-answer**, not tokens-per-call.

| Question the task asks | xmp4 answers? | GitMCP answers? | Context7 answers? | grep+clone answers? |
|---|:---:|:---:|:---:|:---:|
| What is the method signature? | ✓ `xmp4_info docs=summary` | ~ (file path only) | ✓ (curated docs) | ✓ (after `cat`) |
| What is the **actual method body**? | ✓ `xmp4_source` (one call) | ✗ need `fetch_generic_url_content(full-file)` → ~40 000 token | ✗ cannot — doc snippets are curated, not source | ✓ (after `cat`) |
| What are the **real callers** across the whole library? | ✓ `xmp4_callers` → 247 SCIP-resolved in 1 call | ✗ grep-match of string `"run("` → hundreds of false positives, no semantic filter | ✗ **impossible** — Context7 has no call graph | ✗ grep-only — same noise problem as GitMCP |
| Transitive callers (depth 2+)? | ✓ `xmp4_callers(depth=5)` | ✗ impossible | ✗ impossible | ✗ impossible |
| Type hierarchy? | ✓ `xmp4_hierarchy` | ✗ impossible | ✗ impossible | ✗ heuristic grep only |

## Per-repo breakdown — what each backend returned

### spring-boot — `SpringApplication.run`

- **xmp4** (3 calls, 692 tok): class header+doc summary, entire `run(String... args)` method body (50 lines), 247 real callers (first 10 shown, 25 pages available, all SCIP-resolved with exact file:line).
- **grep+clone** (1 clone + 2 grep, 1 039 tok + 73 MB disk + 45s wall): grep hits including README, docs, tests, user code, sample apps. AI must filter which ones are real `run()` invocations vs string matches in comments.
- **GitMCP** (1 call, 287 tok): 30 file paths (out of 143) with URL and Git-blob URL. **No code. No signatures. No callers.** To get the method body the AI must call `fetch_generic_url_content` on the file URL (likely 5 000-20 000 additional tokens).
- **Context7** (2 calls, 323 tok): library ID resolution + curated docs. 3 hello-world examples of `SpringApplication.run(MyApplication.class, args)`. **Does not show the real implementation.** Cannot answer "who calls it in the Spring codebase".

### tokio — `JoinHandle.abort`

- **xmp4**: 414 tok, complete answer in 3 calls (struct doc + method body + 14 real callers across test files).
- **grep+clone**: 685 tok + 8.5 MB disk, `.abort()` matches on many other types.
- **GitMCP**: 150 tok, 20 file paths. No code, no callers.
- **Context7**: 164 tok, docs about `tokio::spawn` returning `JoinHandle`. **No coverage of `.abort()` itself in the response** — Context7 docs didn't return `.abort()` coverage for this query.

### django — `QuerySet.filter`

- **xmp4**: 244 tok, signature + method body (`_filter_or_exclude` delegation) + 3 real internal callers (`get`, `in_bulk`, `contains`).
- **grep+clone**: 368 tok, grep `def filter` matches 10+ unrelated classes.
- **GitMCP**: 117 tok, 30 file paths (296 total). No code, no callers.
- **Context7**: 180 tok, 3 usage examples of `QuerySet.filter` from official docs. **Does not show the implementation and cannot answer "which internal methods delegate to `filter`".**

### efcore — `DbContext.OnConfiguring`

- **xmp4**: 301 tok, class description (UoW+Repository pattern) + empty-body override signature + 3 real callers (including `Finder` + 2 test overrides). Biggest xmp4/grep ratio because EFCore has 6 188 files and grep noise dominates.
- **grep+clone**: 886 tok + 125 MB disk. Grep matches span provider packages, scaffolding, test contexts.
- **GitMCP**: 98 tok, 30 file paths (169 total).
- **Context7**: 149 tok, 3 curated OnConfiguring examples for SQL Server, in-memory, SQLite.

## What the 4 backends are actually good for (honest positioning)

| Backend | Best for | Cannot do |
|---|---|---|
| **xmp4** | *"Understand how the library is built and how to use it correctly"* — real callers, real source, real hierarchy, transitive call graph. | Latest API docs (Context7 wins), ad-hoc text/pattern search (GitMCP/grep win). |
| **GitMCP** | *"Does this string/file exist in the repo?"* and quick file pointers. Fast, cheap. | Cannot return code content in one call (need follow-up), cannot do semantic call graph, cannot filter false positives. |
| **Context7** | *"Give me a hello-world for library X"* — curated, current, well-written docs and examples. | Cannot answer anything about the real library source or its semantic graph. Just docs. |
| **grep+clone** | Deep, local, offline exploration. | Expensive clone setup, noisy results, no semantics. |

## The defensible pitch — revised based on this matrix

**Do NOT claim** *"xmp4 uses fewer tokens than GitMCP or Context7."* It doesn't — per call. A reviewer tests it on a trivial question and gets higher token counts, then assumes all claims are inflated.

**Do say:**

> *"Context7 gives you the docs. GitMCP gives you file pointers. Grep+clone gives you noisy text. Only xmp4 gives you the compiler's answer: the real method body, the real callers, the real type hierarchy — in 3 tool calls, ~600 tokens per question. The other MCPs look cheaper until you realize they can't answer the question without a dozen follow-ups — or at all."*

The complementarity angle works:
- For *"how do I start using X?"* — use Context7.
- For *"what libraries exist around topic Y?"* — use Glama/Cursor Directory.
- For *"how is X actually called, who uses it, what breaks if I change it?"* — use xmp4. Only xmp4.

This is the truth. Publishing it this way on hero/HN is **more credible** than hiding it.

## Follow-up-to-parity cost — the killer stat

Per-call tokens mislead. What matters is **total tokens to reach the same useful answer**. GitMCP's `search_code` returned only file paths — the model still has to fetch the source to see the method body. Measured cost of one `fetch_generic_url_content` on each target file (via live GitMCP call for spring-boot, via tiktoken on the identical local files for the other three):

| Repo | GitMCP search | GitMCP fetch full file | GitMCP total parity | xmp4 total | **GitMCP/xmp4** |
|---|---:|---:|---:|---:|---:|
| spring-boot | 287 | 14 773 | **15 060** | 667 | **22.6×** |
| tokio | 150 | 3 119 | **3 269** | 409 | **8.0×** |
| django | 117 | 23 542 | **23 659** | 249 | **95.0×** |
| efcore | 98 | 23 543 | **23 641** | 233 | **101.5×** |
| **TOTAL** | 652 | **64 977** | **65 629** | **1 558** | **42.1×** |

**GitMCP is 2.5× cheaper per call but 40× more expensive to answer the same question.** And after the 65 629-token fetch, GitMCP *still* cannot produce:

- The **real callers** (would require fetching every candidate caller file and re-grepping — tens of thousands of additional tokens per callsite, and a test-file match is not semantically different from a real invocation).
- The **type hierarchy**.
- **Transitive callers**.

For these three, **no amount of GitMCP calls reaches xmp4's answer.**

Context7 parity is **impossible**. Context7 returns curated doc snippets — not the library's source, not its call graph. No sequence of Context7 calls can answer *"who calls SpringApplication.run inside the spring-boot repo"* because Context7 does not index that information at all.

## The real headline

> **xmp4 vs GitMCP per call: GitMCP is 2.5× cheaper.**
> **xmp4 vs GitMCP to complete answer: GitMCP is 40× more expensive — AND still misses real callers, type hierarchy, and transitive call graph entirely.**
> **xmp4 vs Context7 on semantic questions: Context7 cannot answer them at any price.**

This is the sentence that survives adversarial HN verification. The per-call number loses on paper; the to-parity number wins decisively and correctly frames why xmp4 exists.

## Caveats

- **Task chosen matters.** If we had benchmarked *"find a specific string across docs"*, GitMCP would win decisively. If we had benchmarked *"give me a starter template"*, Context7 would win. xmp4 is designed for *"navigate real code semantically"*, and that is the task this matrix measures.
- **Follow-up cost not yet measured.** To get parity with xmp4's answer, GitMCP would need 1-3 `fetch_generic_url_content` calls (thousands of tokens each). Context7 can't reach parity at any cost for "real callers".
- **xmp4 verbosity is a design choice.** Tool calls are verbose because they take `project`, `symbol_name`, `file_path` — which is exactly what enables the precise SCIP resolution. A compact wrapper-tool could reduce request tokens, but the value is in the precision, not the brevity.

## Next

- Add a **"follow-up-to-parity"** benchmark: simulate the full chain of calls each backend needs to reach xmp4's answer. Expected: GitMCP balloons to 10 000-50 000 tokens per repo, Context7 fails to reach parity.
- Visualize per-repo as grouped bar chart (xmp4 green, others gray) with a "completeness" overlay (✓/✗ per question).
- Re-run on more repos (add angular, flask) to confirm the pattern scales.
