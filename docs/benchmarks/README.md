# xmp4 Token-Saving Benchmark — Methodology v1

**Version**: 1.0-draft · **Date**: 2026-04-20 · **Target server**: xmp4 v1.1.3 at `mcp.example4.ai`

---

## 1. Purpose

Produce **fresh, reproducible, defensible** numbers on how many tokens a semantic MCP server (xmp4) saves an AI coding agent compared to:

- **grep** (ripgrep, the de-facto baseline used by most AI coding tools today)
- **GitMCP** (`gitmcp.io` — a grep-based hosted MCP, currently the closest "no-install" competitor)

Numbers are cited publicly (hero page, Show HN, pitch decks) and **will be adversarially verified** by HN / r/ClaudeAI / Anthropic reviewers. Everything here must re-run bit-identically from a clean checkout.

## 2. What we measure

Primary metric: **tokens consumed by an AI agent to answer one coding question**, including:

- the MCP/grep **response body** the agent must read,
- the MCP/grep **arguments** the agent must emit,
- **all intermediate round-trips** the agent must perform when a single call is insufficient (grep usually requires 2–3 rounds: find, filter, read context).

Secondary metrics:
- **Correctness**: does the final answer contain the canonical symbol/line? How many false positives must be filtered by the model?
- **Wall-clock time per task** (informational — latency is dominated by network, not interesting for the token story).

Tokens are counted with `tiktoken` (`cl100k_base`). This is OpenAI's tokenizer, not Anthropic's, but it is used identically for every backend so **the ratio between backends is unaffected by tokenizer choice**. The methodology will re-run with `anthropic` tokenizer once released to public.

## 3. Repositories under test (5)

Fixed at exact git SHAs to guarantee reproducibility.

| Language | Repository | Tag / SHA | Indexed on xmp4 | Rationale |
|---|---|---|---|---|
| Java | `spring-projects/spring-boot` | _(pin on first run)_ | yes | Gold-standard Java benchmark. Huge symbol graph. |
| TypeScript | `angular/angular` | _(pin)_ | yes (~400K symbols) | Largest pure-TS index live on xmp4. |
| Python | `django/django` | _(pin)_ | yes | De-facto Python benchmark. |
| Rust | `tokio-rs/tokio` | _(pin)_ | yes | Mature crate, well-typed. |
| C# | `dotnet/efcore` | _(pin)_ | yes | Microsoft flagship C#. |

Shallow clones into `./repos/<slug>/` at the pinned SHA for grep baseline.

## 4. Tasks under test (10 — per repo where applicable)

Every task describes a concrete AI-coding-assistant question, not an abstract tool invocation. Each task is scored on all 3 backends.

| # | Task | xmp4 tool | Example query (spring-boot) |
|---|---|---|---|
| 1 | **Find symbol by name** — locate definition | `xmp4_search` | `"ConditionalOnProperty"` |
| 2 | **Find all usages** of a symbol | `xmp4_usages` | `Mono.just` |
| 3 | **Type hierarchy** — who implements/extends X | `xmp4_hierarchy` | `ApplicationContext` |
| 4 | **Callers** — who calls method X | `xmp4_callers` | `SpringApplication.run` |
| 5 | **Callees** — what does method X call | `xmp4_callees` | `ServletWebServerApplicationContext.createWebServer` |
| 6 | **Method body** — source of just method X | `xmp4_source` | `ConfigurationClassPostProcessor.processConfigBeanDefinitions` |
| 7 | **File outline** — members of file X | `xmp4_outline` | `DispatcherServlet.java` |
| 8 | **Pattern search** — symbols matching a convention | `xmp4_search` (regex) | `"*Repository"` |
| 9 | **Tests for symbol** — which tests cover X | `xmp4_tests_for` | `ProductService.save` |
| 10 | **Deps of file** — imports / deps of module X | `xmp4_deps` | `DispatcherServlet.java` |

**Total matrix**: 10 × 5 = 50 task instances (some tasks skipped on repos where they don't apply, e.g. no test-for in tokio benchmarks — documented per run).

## 5. Backends — measurement protocol

For each (task, repo) pair we run all three backends and record a row in `results/YYYY-MM-DD-run.csv`.

### 5.1. xmp4 (hosted MCP @ mcp.example4.ai)

- **One** MCP `tools/call` against the production server.
- **Input tokens** = tokenize the JSON-RPC request body.
- **Output tokens** = tokenize the `result.content[*].text` response body.
- **Rounds**: always 1 (if xmp4 returns more than one round is ever needed to answer, that is itself a finding to record).

### 5.2. grep (ripgrep on locally cloned repo at pinned SHA)

- Simulate a realistic AI-agent workflow: minimum of **search → read context**.
  - Round 1: `rg -n --max-count=200 <pattern> <repo-root>`
  - Round 2 (if result contains a file hit): `rg -n -C <N> <pattern> <file>` or full `head -n <M>` for source extraction tasks.
- **Input tokens** = tokenize the shell command string (the model must emit it).
- **Output tokens** = tokenize the combined stdout of all rounds.
- **False-positive count**: manually tagged lines that do not contain the canonical answer (definitions of other symbols, comments, string literals).

### 5.3. GitMCP (hosted grep MCP)

- Endpoint: `https://gitmcp.io/<owner>/<repo>`.
- Two tools available (per public docs): `fetch_generic_documentation`, `search_generic_code`.
- Measure via MCP `tools/call`, same token rules as xmp4.
- If GitMCP fails / times out / returns empty for a task, log it as `backend_error` — **do not** treat as "winning" for xmp4 in the reported ratio.

All three backends use identical tokenizer (`cl100k_base`) for the token count, so the comparison is apples-to-apples.

## 6. Ground truth & correctness scoring

For each task we pre-define the **canonical answer** (a file + line number or a set of symbol qualified names) extracted from the indexed SCIP data and manually verified against the live source. Each backend response is scored:

- `CORRECT` — canonical answer is contained unambiguously in the output.
- `CORRECT+NOISE` — canonical answer is present but accompanied by ≥1 false positive the model must filter.
- `INCOMPLETE` — canonical answer is missing but some related info is returned.
- `WRONG` — canonical answer absent, output misleading.

Publish rule: **a backend's token savings is only claimed for tasks where its result is CORRECT or CORRECT+NOISE**. INCOMPLETE/WRONG rows are reported separately.

## 7. Reproducibility package

```
benchmarks/
├── README.md                  (this file)
├── tasks.yaml                 definition of 50 (task, repo) cells + ground truth
├── harness.py                 main runner (reads tasks.yaml, writes results CSV)
├── adapters/
│   ├── xmp4_adapter.py        MCP HTTP client against mcp.example4.ai
│   ├── grep_adapter.py        ripgrep + simulated round-trip workflow
│   └── gitmcp_adapter.py      MCP HTTP client against gitmcp.io
├── tokenizer.py               tiktoken wrapper (cl100k_base)
├── repos/                     shallow clones at pinned SHAs (git-ignored)
├── results/
│   └── 2026-04-20-run.csv     one run per date
└── report.md                  human-readable summary generated from latest CSV
```

Any third party can re-run with:

```bash
python harness.py --config tasks.yaml --out results/$(date +%F).csv
python report.py results/latest.csv > report.md
```

## 8. Expected publication artefacts

1. **Public repo** `github.com/0ics-srls/xmp4-benchmarks` — contains everything under `benchmarks/` + a `RESULTS.md` with the latest numbers embedded as a PNG table.
2. **Hero-page numbers** — one headline ratio (e.g. "87% fewer tokens than grep across 50 task-repo cells") — the footnote links to the report.
3. **Pitch to Anthropic/GitHub** — the CSV itself + 1-page narrative.

## 9. Open questions (pre-run decisions)

- [ ] SHA pinning per repo: pin **today's xmp4 index SHA** or pin **each repo's latest release tag at 2026-04-20**? (Leaning: xmp4's own pinned SHA — removes "grep was on different code" objection.)
- [ ] GitMCP rate-limiting: hosted service may throttle a 50-call benchmark burst. Plan: sleep(1s) between calls, single-threaded.
- [ ] Tokenizer caveat: publish `cl100k_base` numbers now, re-run with Anthropic tokenizer once official public — which to cite first on hero?
- [ ] Do we include **"impossible with grep"** tasks (transitive callers, full type hierarchy)? These dominate xmp4's win but are unfair framing. Plan: include in matrix, score grep as `INCOMPLETE`, note separately "4 tasks cannot be solved by grep at all".

## 10. Status

- [ ] Draft methodology (this file) — **in review**
- [ ] `tasks.yaml` with ground truth for 50 cells
- [ ] Adapters coded + smoke-tested on 1 cell per backend
- [ ] Full run + CSV
- [ ] `report.md` generated
- [ ] Promote to public `xmp4-benchmarks` repo

---

_References: lsai-protocol v1.0.9 verification report (`submodules/lsai-protocol/tests/tool-verification-v1.0.9.md`) reported 85 % savings in **bytes** vs grep on a local Zerox.Lsai build. This benchmark supersedes it with token-based measurement on the live xmp4 server._
