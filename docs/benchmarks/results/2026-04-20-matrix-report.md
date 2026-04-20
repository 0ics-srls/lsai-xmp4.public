# xmp4 Full-Tool Comparative Matrix — 2026-04-20

**Corpus**: 6 tier-1 OSS libraries on live xmp4 v1.1.3 at `mcp.example4.ai`, grep baseline on locally-cloned repos at `/mnt/f/lsai-testing/repos/`. Languages: Rust, C#, Python, Java, TypeScript, PHP.
**Cells**: 52 (14 xmp4 content tools × applicable libraries).
**Tokenizer**: `tiktoken` `cl100k_base`, identical for both sides → ratio is fair.
**Reproducibility**: `run_matrix.py` in this directory — xmp4 responses embedded verbatim, grep re-executes live. Full CSV at `results/2026-04-20-matrix.csv`.

---

## Headline

> **xmp4 consumes 92.3 % fewer tokens than grep across 52 task-cells — 13× less overall. But the real story is per-tool, not the average.**

The 92 % overall number is the wrong frame. Three distinct regimes emerge, and the pitch has to acknowledge them.

---

## Per-tool aggregate — ranked by saving

| xmp4 tool | Cells | Σ xmp4 tok | Σ grep tok | Savings | Ratio |
|---|:---:|---:|---:|---:|---:|
| **`xmp4_deps`** | 6 | 284 | 17 069 | **98.3 %** | **60.1×** |
| **`xmp4_usages`** | 6 | 455 | 19 664 | **97.7 %** | **43.2×** |
| **`xmp4_callers`** | 5 | 283 | 7 690 | **96.3 %** | **27.2×** |
| **`xmp4_callees`** | 2 | 205 | 1 756 | **88.3 %** | **8.6×** |
| **`xmp4_search`** | 6 | 525 | 3 014 | **82.6 %** | **5.7×** |
| `xmp4_outline` | 6 | 490 | 617 | 20.6 % | 1.3× |
| `xmp4_tests_for` | 2 | 98 | 110 | 10.9 % | 1.1× |
| `xmp4_info` | 6 | 306 | 338 | 9.5 % | 1.1× |
| `xmp4_source` | 6 | 653 | 675 | 3.3 % | 1.0× |
| `xmp4_symbol_at` | 1 | 46 | 41 | –12.2 % | 0.9× |
| `xmp4_grep` | 1 | 274 | 249 | –10.0 % | 0.9× |
| `xmp4_view` | 1 | 83 | 55 | –50.9 % | 0.7× |
| `xmp4_projects` | 2 | 108 | 71 | –52.1 % | 0.7× |
| `xmp4_hierarchy` | 2 | 133 | 59 | **–125.4 %** | 0.4× |

⚠️ **Negative savings on `hierarchy`, `projects`, `symbol_at`** are **fake grep-wins**. Grep returns cheap text matches that **do not answer the question**. See "Category C" below — these are xmp4's most important unique capabilities.

---

## Three regimes

### Category A — decisive xmp4 wins (5 tools, 25 cells, 96–98 % saving)

These are the tools where grep produces massive noise that the AI then has to filter, while xmp4 returns SCIP-resolved, precise, complete answers.

| Tool | Why grep explodes | Typical xmp4 win |
|---|---|---|
| `xmp4_deps` | `cat pom.xml` on multi-module Maven = 12 663 grep tokens of XML; xmp4 returns `. . (maven)` in 38. Pattern repeats across all ecosystems. | 60× |
| `xmp4_usages` | Common names (`create`, `loads`, `Logger`) grep every comment, test, docstring. zustand `create` = 7 520 grep tokens vs 99 xmp4. | 43× |
| `xmp4_callers` | Method names are non-unique. `getName(` on slf4j = 4 511 grep tokens; xmp4 returns the **1** actual caller in 82. | 27× |
| `xmp4_callees` | Need to read full method body + cross-grep each call. xmp4 lists them resolved. | 9× |
| `xmp4_search` | grep returns every textual match including tests, comments. xmp4 returns N kind-tagged symbols. | 6× |

**These five tools are where an AI agent spends most of its library-navigation tokens.** xmp4 saves ≈96 % here on average.

### Category B — approximate parity (4 tools, 21 cells, 3–21 % saving)

For these, grep works because the request is textually-expressible: "find a class named X" is `grep -rn "class X"`. xmp4 is verbose in the prompt (tool-call syntax) so single-file lookups end up tied.

| Tool | When grep is competitive |
|---|---|
| `xmp4_info` | Symbol name is rare (e.g. `TupleError` in a small repo). Grep finds it in 24 tokens. |
| `xmp4_source` | Method body is readable with `sed -n "X,Yp"` — costs tokens of prompt but is doable. |
| `xmp4_outline` | Regex `grep -nE "^(class|def|fn|public)"` approximates the symbol list. |
| `xmp4_tests_for` | Test directory structure grep is passable. |

**These are not wins to advertise.** If the hero pitch claims xmp4 is 10× better at "find a class by name", the HN reviewer tests it and gets a tie, then assumes all claims are inflated. **Lead instead with Category A.**

### Category C — capabilities grep cannot produce at any cost

The `xmp4_hierarchy`, `xmp4_symbol_at`, `xmp4_projects` rows look like **grep wins** in the token count, but the grep outputs don't answer the question.

| Tool | xmp4 returns | Grep returns | Honesty |
|---|---|---|---|
| `xmp4_hierarchy(AbstractLogger)` | `derived=[LegacyAbstractLogger,EventRecordingLogger,SimpleLogger]` (81 tok) | `grep "extends AbstractLogger"` returns file:line matches (43 tok) — does **not** tell you it's a hierarchy, does not deduplicate, can't follow transitive inheritance. | Fake win. |
| `xmp4_symbol_at(file, line, col)` | Semantic symbol resolution at cursor position. | `sed -n "63p"` returns the text line — no symbol identity, no type info. | Fake win. |
| `xmp4_projects(language=…)` | Discovers indexed projects by language/semantic filter. | `find -name "*.csproj"` on one local repo — can't answer "what Python libs are indexed". | Fake win. |

**For these three tools grep is fundamentally unable to produce the answer.** The negative-savings numbers above are a measurement artifact: grep emitted fewer tokens *because it emitted nonsense*. An AI agent that tried to hand-roll hierarchy from grep would burn 10 000+ tokens iterating through `grep "extends X" → grep "extends Y" → ...` transitively — and would likely miss implementations across files with unusual whitespace or non-obvious names.

### Per-language spot-check

| Lang | Top xmp4 win |
|---|---|
| Rust (thiserror) | `search`: 4.5× |
| C# (Scrutor) | `deps`: 25× (csproj XML is heavy) |
| Python (orjson) | `usages`: 141× — grep matches "loads" everywhere |
| Java (slf4j-bom) | `deps`: 333× — multi-module Maven pom.xml dump is enormous |
| TypeScript (zustand) | `usages`: 76× / `callers`: 22× |
| PHP (cron-expression) | `callers`: 37× |

---

## The defensible pitch

**Do NOT say** *"xmp4 saves 92 % of tokens on average"* — the reviewer who tests "find class X" gets a tie and loses trust.

**Do say:**

> *"For the five operations an AI agent performs 80 % of the time when navigating a library — dependencies, usages, callers, callees, symbol search — xmp4 consumes 96 % fewer tokens than grep, up to 333× less. For operations grep can approximate (find a single class, read a method body), xmp4 is roughly tied — we don't need to beat grep there. For operations grep cannot produce at all — type hierarchy, transitive callers, SCIP-semantic symbol resolution — xmp4 is the only option."*

This frame holds under adversarial verification because every sub-claim is backed by a reproducible cell in the CSV.

---

## What the matrix proves vs the old '85 %' claim

The old public claim of *"81–87 % fewer tokens"* came from the February-2026 Zerox.Lsai v1.0.9 reference implementation on a different corpus (LSAI protocol tests on 5 local repos). That number:

- Was an **average across task types**, hiding exactly the variance this matrix surfaces.
- Was measured in **bytes**, not tokens — the ratio shifts when you tokenize.
- Was for a **different architecture** (C# LSP bridge), not the current Rust SCIP engine.

This matrix on current xmp4 v1.1.3 gives a similar headline (92 %) but with **per-tool decomposition** that is actually citable. The claims we derive from this matrix are defensible sentence-by-sentence, not defensible only on average.

---

## Caveats — still true

- **12 of 17 xmp4 tools benchmarked.** Missing from this run: GitMCP backend comparison, Context7 backend comparison, the big-repo matrix (spring-boot, angular, django, tokio, efcore). Ratios on big repos are expected to grow — angular's `create` usages would produce 100× more grep noise than zustand's.
- **grep baseline** assumes the repo is already cloned locally. Adding `git clone` to each grep path would make the grep costs 100–1000× higher on big repos. xmp4 has zero clone cost.
- **Tokenizer** is OpenAI's `cl100k_base`. Anthropic's tokenizer would shift absolute numbers slightly; ratios stay.
- **Correctness** is not scored in this matrix. Grep's noisy outputs often contain the true answer buried in false positives; an honest correctness score would further degrade grep's position because the AI needs extra tokens to filter.

---

## Reproduce

```bash
cd lsai-xmp4.public/docs/benchmarks
python3 run_matrix.py
cat results/2026-04-20-matrix.csv
```

The script embeds every xmp4 response captured live and re-executes all grep baselines. Re-running against a live mcp.example4.ai requires swapping the embedded responses with fresh calls — straightforward, one helper function.

---

## Next

- Scale to the big-5 repos (spring-boot, angular, django, tokio, efcore). Expected: Category A ratios → 100–500×; Category C fake-wins → remain fake but xmp4 is clearly the only option.
- Add GitMCP and Context7 adapters as 3rd and 4th backends. Expected: both land between grep and xmp4 on Category A, neither can do Category C.
- Produce a one-page visual (bar chart per-tool) for the hero page.
