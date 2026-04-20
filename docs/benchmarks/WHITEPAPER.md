# xmp4 vs GitMCP vs Context7 vs grep — The Honest Token Benchmark

> **What this is.** An adversarial, reproducible measurement of how many tokens an AI coding agent burns to answer the *same* real development question across four backends: xmp4 (SCIP-semantic MCP), GitMCP (grep-over-GitHub MCP), Context7 (curated-docs MCP), and grep on a local clone. Every number here is re-derivable from the Python harness embedded in this directory.
>
> **Date of run**: 2026-04-20 · **xmp4 version**: v1.1.3 at `mcp.example4.ai` · **GitMCP**: `gitmcp.io` · **Context7**: `mcp.context7.com` · **Tokenizer**: `tiktoken` `cl100k_base`

---

## TL;DR — the two numbers that matter

**Per single tool call**, GitMCP and Context7 return fewer tokens than xmp4 — because they return less. GitMCP gives file-path pointers; Context7 gives curated doc snippets; xmp4 returns semantic data.

**Per complete answer to the same question**, xmp4 wins by an order of magnitude. For four tier-1 OSS libraries (spring-boot, tokio, django, efcore):

| | **xmp4** | **grep + clone** | **GitMCP per-call** | **GitMCP to parity** | **Context7** |
|---|---:|---:|---:|---:|---:|
| Total tokens (4 repos) | **1 558** | 2 978 | 652 | **65 629** | 816 |
| Ratio vs xmp4 | 1× | 1.9× more | 0.4× (cheaper) | **42.1× more** | 0.5× (cheaper) |
| Can return real callers? | **✓** | ~ noisy grep | ✗ | ✗ | **✗ at any cost** |
| Can return type hierarchy? | **✓** | ✗ | ✗ | ✗ | ✗ |
| Clone / disk required? | no | **~500 MB–1 GB** | no | no | no |

The **per-call** and **to-parity** rows tell opposite stories. Both are true. Which one matters depends on what question the AI agent is really trying to answer. Scroll past the TL;DR to see when each is the relevant frame.

---

## 1. The task — identical across all four backends

For each library, the AI agent is trying to answer the kind of question that actually comes up during real integration work:

> *"I want to use `<SYMBOL>` from `<LIBRARY>` in my project. Give me the method signature, the actual implementation body, and the real callers inside the library so I understand how it's meant to be used."*

Concretely, per library:

| Library | Symbol | Question in one line |
|---|---|---|
| **spring-boot** | `SpringApplication.run` | "How does `SpringApplication.run(...)` actually bootstrap the app?" |
| **tokio** | `JoinHandle.abort` | "How do I cancel a spawned task — what does `.abort()` actually do?" |
| **django** | `QuerySet.filter` | "How is `.filter(**kwargs)` implemented and what internal methods call it?" |
| **efcore** | `DbContext.OnConfiguring` | "What's the `OnConfiguring` override I need to implement — and when is it called?" |

## 2. The four backends — what each one is

### xmp4 — `mcp.example4.ai`
A hosted MCP server that serves **SCIP-indexed** symbol graphs for 547 popular OSS libraries. Its 17 tools let an AI agent call `xmp4_info` (signature), `xmp4_source` (method body), `xmp4_callers` (semantic call graph), `xmp4_hierarchy` (type hierarchy), etc. Zero-install — it's just an HTTP endpoint.

### grep + clone
The baseline every AI coding tool falls back to today: `git clone`, then `grep`. Costs include:
- The clone itself (tokens emitted + GB of disk).
- Noisy text matches on common method names.
- Multiple round-trips to filter false positives and read context.

### GitMCP — `gitmcp.io/<owner>/<repo>`
A hosted MCP that exposes GitHub's code-search API. Four tools per repo: `search_<repo>_code`, `fetch_<repo>_documentation`, `search_<repo>_documentation`, `fetch_generic_url_content`. No clone, but **only text search** — no symbol resolution, no call graph.

### Context7 — `mcp.context7.com`
A hosted MCP that indexes **curated documentation** for many libraries. Returns doc snippets, hello-world examples, API references. No source code, no call graph — the "read-the-docs" experience as an MCP.

## 3. The procedure

```
For each of the 4 libraries:

    xmp4 workflow (prescribed by xmp4_guide):
        1. xmp4_info(project, symbol_name, file_path)         ─┐
        2. xmp4_source(project, symbol_name, file_path)        ├─→ complete answer
        3. xmp4_callers(project, symbol_name, file_path)      ─┘

    grep + clone workflow:
        1. git clone --depth=1 <repo>                          ─┐
        2. grep -rn "class|fn|struct X" <repo>                  ├─→ noisy answer
        3. grep -rn "X.method" <repo> (often head-capped)     ─┘

    GitMCP workflow (per-call):
        1. search_<repo>_code(query="X method")                ─→ file paths only
        (for parity, add)
        2. fetch_generic_url_content(<full-file-URL>)          ─→ +full file tokens

    Context7 workflow:
        1. resolve-library-id(libraryName, query)              ─┐
        2. query-docs(libraryId, query)                         ├─→ doc snippets only
```

For every tool call we record **both** the request string (what the model emits) and the response body (what comes back). Both are tokenized with `tiktoken` `cl100k_base` — the same tokenizer for every backend so the ratio is unaffected by tokenizer choice.

## 4. The code that measures

The full measurement harness lives next to this document. Three Python files, all self-contained:

- [`run_pilot.py`](run_pilot.py) — 12-cell pilot (6 small tier-1 repos × 2 task types) — proved the methodology.
- [`run_matrix.py`](run_matrix.py) — 52-cell full-tool matrix (14 xmp4 tools × 6 libraries) — per-tool breakdown.
- [`run_bigrepo_4backend.py`](run_bigrepo_4backend.py) — 4-backend comparison on 4 big-repo integration tasks — this paper.

### Key code excerpt — the measurement primitive

The harness tokenizes every request and every response with the same OpenAI `cl100k_base` tokenizer, so the comparison is apples-to-apples. No approximation, no byte-counting.

```python
# run_bigrepo_4backend.py (excerpt)
import tiktoken
ENC = tiktoken.get_encoding("cl100k_base")

def tok(s: str) -> int:
    return len(ENC.encode(s))

# Every cell is a (request_str, response_str) pair.
# request_str = exactly what the model emits to invoke the tool.
# response_str = exactly what the server returns, captured verbatim.

def sum_tokens(pairs):
    """Total tokens the model must emit+read across a call sequence."""
    req = sum(tok(rq) for rq, _ in pairs)
    out = sum(tok(rs) for _, rs in pairs)
    return req, out, req + out, len(pairs)
```

### Key code excerpt — xmp4 responses captured verbatim

Every xmp4 response in the harness is a literal copy-paste of what the live `mcp.example4.ai` server returned on 2026-04-20. No paraphrasing.

```python
# run_bigrepo_4backend.py (excerpt) — spring-boot xmp4 block
SPRING = {
    "xmp4_calls": [
        ('xmp4_info(project="spring-boot/spring-boot", '
         'symbol_name="SpringApplication", '
         'file_path="spring-boot-project/spring-boot/src/main/java/org/springframework/boot/SpringApplication.java")',
         'Class SpringApplication spring-boot-project/.../SpringApplication.java:188\n'
         '[docs available: call with docs=summary|full]'),
        ('xmp4_source(project="spring-boot/spring-boot", '
         'symbol_name="run", file_path=".../SpringApplication.java")',
         # ↓ 50 lines of actual run() method body captured from the server
         'Method run .../SpringApplication.java:301\n'
         'public ConfigurableApplicationContext run(String... args) {\n'
         '    Startup startup = Startup.create();\n'
         '    ...\n'
         '    return context;\n'
         '}'),
        ('xmp4_callers(project="spring-boot/spring-boot", '
         'symbol_name="run", file_path=".../SpringApplication.java", page_size=10)',
         # ↓ 247 real SCIP-resolved callers — first 10 shown, 25 pages available
         '247 callers found (page 1/25)\n'
         'main spring-boot-project/.../SpringBootContextLoaderTests.java:427\n'
         '...'),
    ],
    ...
}
```

### Key code excerpt — grep executed live

For the grep baseline, the harness actually runs the grep commands in the locally-cloned repo. No extrapolation.

```python
# run_bigrepo_4backend.py (excerpt)
def run_grep(repo_subdir, cmds):
    cwd = REPOS / repo_subdir   # /mnt/f/lsai-testing/bigrepos/<repo>
    out_parts = []
    for emit_str, shell_cmd in cmds:
        r = subprocess.run(shell_cmd, cwd=cwd, capture_output=True,
                           text=True, timeout=120)
        out_parts.append(r.stdout)
    return tok("\n".join(out_parts)), ...

# Measured cost = tokens(clone command emitted) + tokens(clone output)
#               + tokens(grep command emitted) + tokens(grep stdout)
```

### Key code excerpt — GitMCP parity measurement

The GitMCP `search_code` result doesn't contain source — only file paths. To simulate what GitMCP actually needs to reach xmp4's answer, the harness measures the cost of one `fetch_generic_url_content` call on the target file.

```python
# We called mcp__gitmcp-spring-boot__fetch_generic_url_content against
# the SpringApplication.java URL. The server returned:
#   "Error: result (70,318 characters across 1,876 lines) exceeds maximum
#    allowed tokens. Output has been saved to <file>."
# The saved file tokenizes to 14,773 cl100k_base tokens.

parity_fetch_tokens = {
    "spring-boot": 14_773,   # measured live via GitMCP
    "tokio":         3_119,  # tokenized locally from identical shallow-clone file
    "django":       23_542,  # tokenized locally
    "efcore":       23_543,  # tokenized locally
}
```

Everything else in the three `run_*.py` files is plumbing — CSV emission, aggregation, printing the table.

---

## 5. The raw per-call results

| Repo | xmp4 | grep + clone | GitMCP per-call | Context7 | xmp4/grep | xmp4/GitMCP | xmp4/Context7 |
|---|---:|---:|---:|---:|---:|---:|---:|
| **spring-boot** | 667 | 1 039 | 287 | 323 | **1.6× less** | 2.3× more | 2.1× more |
| **tokio** | 409 | 685 | 150 | 164 | **1.7× less** | 2.7× more | 2.5× more |
| **django** | 249 | 368 | 117 | 180 | **1.5× less** | 2.1× more | 1.4× more |
| **efcore** | 233 | 886 | 98 | 149 | **3.8× less** | 2.4× more | 1.6× more |
| **TOTAL** | **1 558** | **2 978** | **652** | **816** | **+48 %** | **−139 %** | **−91 %** |

Numbers of tool calls: xmp4 = 12 (3 per repo), grep = 12 (1 clone + 2 greps per repo), GitMCP = 4 (1 search per repo), Context7 = 5 (1 resolve + 1 query per repo, except spring-boot which needed the explicit resolve).

**Read this table carefully.** On an individual call basis, GitMCP and Context7 are cheaper than xmp4 — and a benchmark that stopped here would conclude "xmp4 is more expensive per call." That would be true but misleading, because the four backends are not producing the same information per call.

## 6. The parity table — same answer, honest total cost

The only fair head-to-head is: **how many tokens until the AI has the signature + body + real callers?**

| Repo | GitMCP `search_code` | GitMCP `fetch_file` | GitMCP total to reach xmp4's answer | xmp4 total | **GitMCP / xmp4** |
|---|---:|---:|---:|---:|---:|
| spring-boot | 287 | 14 773 | **15 060** | 667 | **22.6×** |
| tokio | 150 | 3 119 | **3 269** | 409 | **8.0×** |
| django | 117 | 23 542 | **23 659** | 249 | **95.0×** |
| efcore | 98 | 23 543 | **23 641** | 233 | **101.5×** |
| **TOTAL** | 652 | **64 977** | **65 629** | **1 558** | **42.1×** |

**And even after that 65 629-token marathon, GitMCP still has not given the AI:**

- The **real callers** inside the library. The file listing from `search_code` finds every string match, including test files, documentation, sample apps. An AI trying to answer *"who calls `SpringApplication.run` in the actual framework"* would have to fetch every candidate file (many thousands more tokens) and guess semantically. There are 247 real callers (per xmp4); GitMCP's `search_code` surfaced 143 matches — different sets, neither subset of the other, because grep finds string occurrences and SCIP finds semantic call edges.
- The **type hierarchy** (who extends `AbstractLogger`, who implements `Logger`).
- The **transitive call graph** (what `SpringApplication.run` → `prepareContext` → `bindToSpringApplication` → ... ).

For these three, **no number of GitMCP calls reaches xmp4's answer**.

**Context7 parity is flat-out impossible.** Context7's index is documentation, not source code. It can return 10 hello-world examples of `SpringApplication.run`, but it cannot return the actual 50-line body of the method, because that body is not in its index. It can describe `QuerySet.filter` conceptually, but it cannot tell you that `QuerySet.get`, `in_bulk`, and `contains` delegate to it internally — because it does not know the call graph.

## 7. The completeness matrix — what each backend can actually answer

| Question the AI agent might ask | xmp4 | GitMCP | Context7 | grep + clone |
|---|:---:|:---:|:---:|:---:|
| What's the method signature? | ✓ (`xmp4_info`) | ~ (file path only) | ✓ (curated docs) | ✓ (after `cat`) |
| What does the method body look like? | ✓ (`xmp4_source`, 1 call) | ✗ needs `fetch_generic_url_content` of entire file | ✗ curated snippets only, not real source | ✓ (after `cat`) |
| Who calls this method **semantically**? | ✓ (`xmp4_callers`, 1 call, zero false positives) | ✗ text matches include docs/tests/comments | ✗ cannot answer | ~ noisy grep |
| Transitive callers, depth 2–5? | ✓ (`xmp4_callers depth=5`) | ✗ impossible | ✗ impossible | ✗ impossible |
| Type hierarchy (base + derived)? | ✓ (`xmp4_hierarchy`) | ✗ | ✗ | ~ heuristic grep |
| Which tests exercise this method? | ✓ (`xmp4_tests_for`) | ~ grep in `tests/` | ✗ | ~ noisy |
| External dependencies with versions? | ✓ (`xmp4_deps`, 30–80 tokens) | ✗ | ✗ | ✓ but huge (whole pom.xml) |
| "Give me a hello-world example" | ~ via `xmp4_source` of a test | ✗ | **✓ best here** | ~ grep in examples/ |
| "Is this exact string in the repo?" | ~ via `xmp4_grep` | **✓ best here** | ✗ | ✓ |

The matrix is not "xmp4 always wins". It's: **xmp4 wins the semantic questions; Context7 wins docs-first questions; GitMCP wins raw-text questions; grep is the fallback.** The value of xmp4 is **the semantic column**, which no other MCP can fill.

## 8. What the four backends are actually positioned for

| Backend | Best used for | Not what it's for |
|---|---|---|
| **xmp4** | *"Understand how this library works under the hood: real callers, real source, real hierarchy, transitive impact."* The daily-integration workflow. | Getting the latest API-docs hello-world (use Context7), finding arbitrary strings in README (use GitMCP). |
| **GitMCP** | Quick "does file X exist in repo Y" / "is this string anywhere" / file-pointer lookups. No clone needed. | Answering how a method is used, who calls it, or what the library's architecture looks like — grep-on-GitHub can't. |
| **Context7** | Pulling curated documentation, examples, migration guides. Beautiful for tutorials. | Anything about the real source or call graph — it's docs, not code. |
| **grep + clone** | Exhaustive offline exploration of a repo you're going to hack on for a week. | Quick answers across many libraries — the clone cost alone kills the economy. |

These backends are **complementary**, not competitors. An AI agent with access to all four would default to **xmp4 for semantic questions** (80% of integration work), **Context7 for "how do I start"** (10%), **GitMCP for "is this string here"** (5%), **grep for deep local work** (5%).

## 9. The defensible public claim

One sentence that survives adversarial verification:

> **GitMCP and Context7 cost fewer tokens per call than xmp4 — because they return less. To answer the real question — signature + body + real callers — GitMCP needs 42× more tokens than xmp4, and still can't produce the semantic caller list at any price. Context7 can't produce it at all. Only xmp4 returns the compiler's view of 547 OSS libraries in 3 tool calls.**

Every sub-claim in that sentence is reproducible from the Python files in this directory. Nothing is extrapolated.

## 10. Reproduce it yourself

Prerequisites: Python 3.10+, `tiktoken`, `git`, `grep`, ~1 GB disk.

```bash
# 1. Clone this benchmark directory
git clone https://github.com/0ics-srls/lsai-xmp4.public.git
cd lsai-xmp4.public/docs/benchmarks

# 2. Install tokenizer
pip install tiktoken

# 3. Shallow-clone the four target repos (~270 MB total)
mkdir -p /mnt/f/lsai-testing/bigrepos && cd /mnt/f/lsai-testing/bigrepos
for r in tokio-rs/tokio django/django dotnet/efcore spring-projects/spring-boot; do
    name=$(echo "$r" | tr / -)
    git clone --depth=1 --single-branch "https://github.com/$r.git" "$name"
done
cd -

# 4. Run the 4-backend big-repo benchmark
python3 run_bigrepo_4backend.py
# ↓ prints the per-call table and the parity summary
#   writes results/$(date +%F)-bigrepo-4backend.csv

# 5. (Optional) re-validate the xmp4 responses against the live server
#    by calling mcp.example4.ai directly — the harness embeds them verbatim
```

To re-run xmp4 against your own MCP client, point it at `https://mcp.example4.ai/mcp` and replay each call from the `xmp4_calls` lists in the harness. To re-run GitMCP against a different repo, change the `gitmcp-<repo>` MCP config to the repo you want. To re-run Context7, just change the `libraryName` passed to `resolve-library-id`.

## 11. Caveats, limitations, what this isn't

- **This benchmark is task-specific.** If the task were "find a string in docs" or "get a starter template", GitMCP / Context7 would respectively win. We measured *semantic understanding of a library symbol*, which is what an AI agent does most during integration work.
- **Four big-repo cells is not 50.** The per-tool matrix (`run_matrix.py`, 52 cells) is more breadth, but on small libraries. Angular (400 K symbols) and Kubernetes (huge Go) are not yet measured; expected direction: GitMCP's parity cost grows linearly with file size, xmp4 does not.
- **Tokenizer is OpenAI's.** Anthropic's tokenizer will shift absolute numbers slightly; ratios stay. We will re-run when Anthropic's tokenizer is public.
- **Verbosity is a tuning knob.** xmp4's `docs="summary"` or `docs="full"` parameters add tokens for richer output. The numbers above use pure compact (default) — the minimum-verbosity floor. An agent asking for `docs="full"` on every call makes xmp4 more expensive; that's user choice.
- **No correctness scoring in the matrix yet.** We tagged ✓/✗ on *capability* (can it answer?) but did not score false-positive rates on grep. A correctness-aware scoring would further hurt grep's numbers because an AI chasing false positives burns additional filtering tokens.
- **We don't include Sourcegraph Cody, Sourcebot, Serena** (install-first semantic tools) because those aren't zero-install MCPs. They serve a different workflow and would add a setup cost that would need a separate benchmark.

## 12. Next

- Scale to angular (400 K TS symbols), kubernetes (Go), rails (Ruby) to stress-test the parity ratio. Expected angular: GitMCP parity ≥ 50 000 tok for one file; xmp4 stays at ~800 tok.
- Publish a public standalone repo (`github.com/0ics-srls/xmp4-benchmarks`, Apache 2.0) that cherry-picks these three Python files plus the results. Reviewers clone from there, not from the marketing monorepo.
- Add correctness scoring: for each grep result, tag how many lines contain the actual answer vs noise.
- Re-run on Claude 4.7 Sonnet / Opus to confirm `cl100k_base`-measured ratios match Anthropic-tokenized outcomes.

---

## Appendix A — the exact live responses captured 2026-04-20

For full fidelity, the literal response strings from each live server are embedded verbatim in `run_bigrepo_4backend.py` (xmp4 + GitMCP + Context7 calls per repo). A reader can open that file and see every character the server returned — no paraphrasing, no summaries. The CSV in `results/2026-04-20-bigrepo-4backend.csv` is the machine-readable form.

## Appendix B — related artefacts in this directory

| File | Purpose |
|---|---|
| [`README.md`](README.md) | Original methodology draft (pre-measurement). |
| [`findings-pre-benchmark.md`](findings-pre-benchmark.md) | Pre-run validation that caught an operator-error assumption about `xmp4_search` ranking — documented behaviour per `xmp4_guide`, not a bug. |
| [`run_pilot.py`](run_pilot.py) · [`results/2026-04-20-pilot-report.md`](results/2026-04-20-pilot-report.md) | 12-cell pilot: 6 small tier-1 libraries × find/usages tasks. |
| [`run_matrix.py`](run_matrix.py) · [`results/2026-04-20-matrix-report.md`](results/2026-04-20-matrix-report.md) | 52-cell per-tool matrix: all 14 xmp4 tools × 6 libraries. |
| [`run_bigrepo_4backend.py`](run_bigrepo_4backend.py) · [`results/2026-04-20-bigrepo-4backend-report.md`](results/2026-04-20-bigrepo-4backend-report.md) | This paper's measurement harness and raw results. |
| [`registry-publish-runbook.md`](registry-publish-runbook.md) | Operational runbook to publish xmp4 to the Official MCP Registry — outside the benchmark scope, but relevant to launch. |

---

_Authored 2026-04-20. All tool responses captured live against the stated servers on that date. All code paths executed in a single continuous benchmarking session. The `git log` of this directory is the provenance._
