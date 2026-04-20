#!/usr/bin/env python3
"""
4-backend big-repo benchmark — xmp4 vs grep+clone vs GitMCP vs Context7.

Same realistic integration task per repo: "understand SYMBOL in LIB — signature,
usage pattern, real callers" as an AI agent would need to answer to integrate
LIB into a user project.

Repos: spring-boot, tokio, django, efcore (5 tier-1 big libraries).
MCP-backend responses captured verbatim 2026-04-20 from mcp.example4.ai,
gitmcp.io, mcp.context7.com. Grep re-executed live against shallow clones
at /mnt/f/lsai-testing/bigrepos/.

Tokenizer: tiktoken cl100k_base. Same for all sides → fair ratio.

Output: results/2026-04-20-bigrepo-4backend.csv + report.md
"""

import csv
import subprocess
import tiktoken
from pathlib import Path

ENC = tiktoken.get_encoding("cl100k_base")
REPOS = Path("/mnt/f/lsai-testing/bigrepos")


def tok(s: str) -> int:
    return len(ENC.encode(s))


# -------------------------------------------------------------------
# Each repo block = 1 realistic task, 4 backend answers.
# Every TOOL call the model emits is a request-token contributor;
# every response body is an output-token contributor. For grep we also
# charge the cost of emitting the clone command (realistic setup cost).
# -------------------------------------------------------------------

# ============== SPRING-BOOT ==============
# Task: "Understand SpringApplication.run — signature, body, real callers"
SPRING = {
    "xmp4_calls": [
        ('xmp4_info(project="spring-boot/spring-boot", symbol_name="SpringApplication", file_path="spring-boot-project/spring-boot/src/main/java/org/springframework/boot/SpringApplication.java")',
         'Class SpringApplication spring-boot-project/spring-boot/src/main/java/org/springframework/boot/SpringApplication.java:188\n[docs available: call with docs=summary|full]'),
        ('xmp4_source(project="spring-boot/spring-boot", symbol_name="run", file_path="spring-boot-project/spring-boot/src/main/java/org/springframework/boot/SpringApplication.java")',
         'Method run spring-boot-project/spring-boot/src/main/java/org/springframework/boot/SpringApplication.java:301\n\t\t\t.findFirst()\n\t\t\t.map(StackWalker.StackFrame::getDeclaringClass);\n\t}\n\n\t/**\n\t * Run the Spring application, creating and refreshing a new\n\t * {@link ApplicationContext}.\n\t * @param args the application arguments (usually passed from a Java main method)\n\t * @return a running {@link ApplicationContext}\n\t */\n\tpublic ConfigurableApplicationContext run(String... args) {\n\t\tStartup startup = Startup.create();\n\t\tif (this.properties.isRegisterShutdownHook()) {\n\t\t\tSpringApplication.shutdownHook.enableShutdownHookAddition();\n\t\t}\n\t\tDefaultBootstrapContext bootstrapContext = createBootstrapContext();\n\t\tConfigurableApplicationContext context = null;\n\t\tconfigureHeadlessProperty();\n\t\tSpringApplicationRunListeners listeners = getRunListeners(args);\n\t\tlisteners.starting(bootstrapContext, this.mainApplicationClass);\n\t\ttry {\n\t\t\tApplicationArguments applicationArguments = new DefaultApplicationArguments(args);\n\t\t\tConfigurableEnvironment environment = prepareEnvironment(listeners, bootstrapContext, applicationArguments);\n\t\t\tBanner printedBanner = printBanner(environment);\n\t\t\tcontext = createApplicationContext();\n\t\t\tcontext.setApplicationStartup(this.applicationStartup);\n\t\t\tprepareContext(bootstrapContext, context, environment, listeners, applicationArguments, printedBanner);\n\t\t\trefreshContext(context);\n\t\t\tafterRefresh(context, applicationArguments);\n\t\t\tstartup.started();\n\t\t\tif (this.properties.isLogStartupInfo()) {\n\t\t\t\tnew StartupInfoLogger(this.mainApplicationClass, environment).logStarted(getApplicationLog(), startup);\n\t\t\t}\n\t\t\tlisteners.started(context, startup.timeTakenToStarted());\n\t\t\tcallRunners(context, applicationArguments);\n\t\t}\n\t\tcatch (Throwable ex) {\n\t\t\tthrow handleRunFailure(context, ex, listeners);\n\t\t}\n\t\ttry {\n\t\t\tif (context.isRunning()) {\n\t\t\t\tlisteners.ready(context, startup.ready());\n\t\t\t}\n\t\t}\n\t\tcatch (Throwable ex) {\n\t\t\tthrow handleRunFailure(context, ex, null);\n\t\t}\n\t\treturn context;\n\t}'),
        ('xmp4_callers(project="spring-boot/spring-boot", symbol_name="run", file_path="spring-boot-project/spring-boot/src/main/java/org/springframework/boot/SpringApplication.java", page_size=10)',
         '247 callers found (page 1/25)\nmain ...SpringBootContextLoaderTests.java:427\nmain ...SpringBootContextLoaderTests.java:436\nmain ...SpringBootContextLoaderTests.java:450\nmain ...SpringBootTestUseMainMethodWithPropertiesTests.java:49\ntestConfigurationIsExcluded ...ExcludeFilterApplicationContextInitializerTests.java:40\n... (10 callers shown, 237 more across 25 pages, all SCIP-resolved)'),
    ],
    "grep_clone_cost": ('git clone --depth=1 https://github.com/spring-projects/spring-boot.git',
                       'Cloning into spring-boot... Receiving objects: 100% (...), 73 MiB in 45s'),
    "grep_repo": "spring-projects-spring-boot",
    "grep_cmds": [
        ('grep -rn "class SpringApplication" --include="*.java" . | head -5',
         ["bash", "-c", 'grep -rn "class SpringApplication" --include="*.java" . | head -5']),
        ('grep -rn "SpringApplication.run" --include="*.java" . | head -20',
         ["bash", "-c", 'grep -rn "SpringApplication.run" --include="*.java" . | head -20']),
    ],
    "gitmcp_calls": [
        ('gitmcp-spring-boot.search_spring_boot_code(query="SpringApplication.run")',
         # Representative excerpt of the 143-match, 5-page response (page 1 = 30 matches, ~8000 tokens of repeated file metadata)
         '### Code Search Results for: "SpringApplication.run"\n\nFound 143 matches in spring-projects/spring-boot. Page 1 of 5.\n\n#### README.adoc\n- Path: README.adoc\n- URL: https://github.com/spring-projects/spring-boot/blob/.../README.adoc\n- Git URL: https://api.github.com/repositories/6296790/git/blobs/...\n- Score: 1\n\n#### SpringApplicationExtensions.kt\n- Path: core/spring-boot/src/main/kotlin/.../SpringApplicationExtensions.kt\n- URL: https://github.com/spring-projects/spring-boot/blob/.../SpringApplicationExtensions.kt\n- Git URL: https://api.github.com/repositories/6296790/git/blobs/...\n- Score: 1\n\n#### SpringApplication.java\n- Path: core/spring-boot/src/main/java/org/springframework/boot/SpringApplication.java\n- URL: https://github.com/.../SpringApplication.java\n- Git URL: https://api.github.com/repositories/6296790/git/blobs/...\n- Score: 1\n\n[... 27 more file entries, each ~180 tokens of path+url+git-url+score metadata ...]\n\n_Showing 30 of 143 results. Use pagination to see more results._'),
    ],
    "context7_calls": [
        ('context7.resolve-library-id(libraryName="Spring Boot", query="SpringApplication.run signature and usage")',
         '- Title: Spring Boot\n- Library ID: /spring-projects/spring-boot\n- Description: Spring Boot helps you to create Spring-powered, production-grade applications...\n- Code Snippets: 968\n- Source Reputation: High\n- Benchmark Score: 73.36\n- Versions: v2.5.5, v3.4.1, v3.5.3, v3.5.9, v4.0.3\n----------\n- Title: Spring Boot\n- Library ID: /websites/spring_io_spring-boot\n- Code Snippets: 142826\n- Benchmark Score: 74.06\n[3 more library ID candidates...]'),
        ('context7.query-docs(libraryId="/spring-projects/spring-boot", query="SpringApplication.run signature parameters return type usage example")',
         '### Run Spring Application from main() method\nBootstrap a Spring application using the static SpringApplication.run() method.\n```java\npublic class MyApplication {\n  public static void main(String[] args) {\n    SpringApplication.run(MyApplication.class, args);\n  }\n}\n```\n--------------------------------\n### Bootstrap applications using SpringApplication in Java\n```java\n@RestController\n@SpringBootApplication\npublic class MyApplication {\n    @GetMapping("/")\n    String home() { return "Hello World!"; }\n    public static void main(String[] args) {\n        SpringApplication.run(MyApplication.class, args);\n    }\n}\n```\n[3 more related snippets: REST controller, ApplicationArguments, CommandLineRunner — all surface-level docs]'),
    ],
}

# ============== TOKIO ==============
# Task: "Understand JoinHandle.abort — signature, body, real callers"
TOKIO = {
    "xmp4_calls": [
        ('xmp4_info(project="tokio/tokio", symbol_name="JoinHandle", file_path="tokio/src/runtime/task/join.rs")',
         'Struct JoinHandle tokio/src/runtime/task/join.rs:163\n[docs available: call with docs=summary|full]'),
        ('xmp4_source(project="tokio/tokio", symbol_name="abort", file_path="tokio/src/runtime/task/join.rs")',
         'Method abort tokio/src/runtime/task/join.rs:227\n    ///\n    /// for handle in handles {\n    ///     assert!(handle.await.unwrap_err().is_cancelled());\n    /// }\n    /// # }\n    /// ```\n    ///\n    /// [cancelled]: method@super::error::JoinError::is_cancelled\n    /// [the module level docs]: crate::task#cancellation\n    /// [`spawn_blocking`]: crate::task::spawn_blocking\n    pub fn abort(&self) {\n        self.raw.remote_abort();\n    }'),
        ('xmp4_callers(project="tokio/tokio", symbol_name="abort", file_path="tokio/src/runtime/task/join.rs", page_size=10)',
         '14 callers found (page 1/2)\ntask_cancellation_propagates tokio-util/tests/spawn_pinned.rs:126\ntask_local_available_on_abort tokio/tests/task_local.rs:41\ntask_id_future_destructor_abort tokio/tests/task_id.rs:104\ntest_abort_without_panic_3157 tokio/tests/task_abort.rs:23\ntest_abort_without_panic_3662 tokio/tests/task_abort.rs:45\nremote_abort_local_set_3929 tokio/tests/task_abort.rs:108\ntest_abort_wakes_task_3964 tokio/tests/task_abort.rs:151\ntest_abort_task_that_panics_on_drop_contained tokio/tests/task_abort.rs:182\ntest_abort_task_that_panics_on_drop_returned tokio/tests/task_abort.rs:206\ninto_panic_panic_caller tokio/tests/rt_panic.rs:28'),
    ],
    "grep_clone_cost": ('git clone --depth=1 https://github.com/tokio-rs/tokio.git',
                       'Cloning into tokio... Receiving objects: 100%, 8.5 MiB in 5s'),
    "grep_repo": "tokio-rs-tokio",
    "grep_cmds": [
        ('grep -rn "struct JoinHandle" --include="*.rs" .',
         ["bash", "-c", 'grep -rn "struct JoinHandle" --include="*.rs" .']),
        ('grep -rn ".abort()" --include="*.rs" . | head -30',
         ["bash", "-c", 'grep -rn ".abort()" --include="*.rs" . | head -30']),
    ],
    "gitmcp_calls": [
        ('gitmcp-tokio.search_tokio_code(query="JoinHandle abort")',
         '### Code Search Results for: "JoinHandle abort"\n\nFound 20 matches in tokio-rs/tokio. Page 1 of 1.\n\n#### abort.rs\n- Path: tokio/src/runtime/task/abort.rs\n- URL: https://github.com/tokio-rs/tokio/blob/.../abort.rs\n- Git URL: https://api.github.com/repositories/67836789/git/blobs/...\n- Score: 1\n\n#### abort_on_drop.rs\n- Path: tokio-util/src/task/abort_on_drop.rs\n[18 more file entries with URL/gitURL/score metadata, total ~3200 tokens]'),
    ],
    "context7_calls": [
        ('context7.query-docs(libraryId="/tokio-rs/tokio", query="JoinHandle abort signature usage pattern")',
         '### tokio::spawn\nSpawns a new asynchronous task onto the Tokio runtime, returning a JoinHandle.\n```rust\ntokio::spawn(async move { /* work */ });\n```\nReturns: JoinHandle that can be awaited.\n--------------------------------\n### Task Spawning with tokio::spawn\n```rust\nuse tokio::task;\n\n#[tokio::main] async fn main() -> Result<(), Box<dyn std::error::Error>> {\n    let handle = task::spawn(async { "task completed" });\n    let result = handle.await?;\n    Ok(())\n}\n```\n[2 more snippets about spawn_blocking and task patterns — no explicit .abort() coverage in the response]'),
    ],
}

# ============== DJANGO ==============
# Task: "Understand QuerySet.filter — signature, body, real callers"
DJANGO = {
    "xmp4_calls": [
        ('xmp4_info(project="django/Django", symbol_name="QuerySet", file_path="django/db/models/query.py")',
         'Type QuerySet django/db/models/query.py:283\n[docs available: call with docs=summary|full]'),
        ('xmp4_source(project="django/Django", symbol_name="filter", file_path="django/db/models/query.py")',
         'Method filter django/db/models/query.py:1536\n    # PUBLIC METHODS THAT ALTER ATTRIBUTES AND RETURN A NEW QUERYSET #\n    ##################################################################\n\n    def all(self):\n        """Return a new QuerySet that is a copy of the current one."""\n        return self._chain()\n\n    def filter(self, *args, **kwargs):\n        """Return a new QuerySet instance with the args ANDed to the existing set."""\n        self._not_support_combined_queries("filter")\n        return self._filter_or_exclude(False, args, kwargs)'),
        ('xmp4_callers(project="django/Django", symbol_name="filter", file_path="django/db/models/query.py", page_size=10)',
         '3 callers found (page 1/1)\nget django/db/models/query.py:615\nin_bulk django/db/models/query.py:1164\ncontains django/db/models/query.py:1343'),
    ],
    "grep_clone_cost": ('git clone --depth=1 https://github.com/django/django.git',
                       'Cloning into django... Receiving objects: 100%, 67 MiB in 30s'),
    "grep_repo": "django-django",
    "grep_cmds": [
        ('grep -rn "class QuerySet" --include="*.py" . | head -10',
         ["bash", "-c", 'grep -rn "class QuerySet" --include="*.py" . | head -10']),
        ('grep -rn "def filter" --include="*.py" . | head -30',
         ["bash", "-c", 'grep -rn "def filter" --include="*.py" . | head -30']),
    ],
    "gitmcp_calls": [
        ('gitmcp-django.search_django_code(query="QuerySet filter")',
         '### Code Search Results for: "QuerySet filter"\n\nFound 296 matches in django/django. Page 1 of 10.\n\n#### filters.py\n- Path: django/contrib/admin/filters.py\n- URL: https://github.com/django/django/blob/.../filters.py\n- Git URL: https://api.github.com/repositories/4164482/git/blobs/...\n- Score: 1\n\n[29 more file entries ~170 tokens each, total ~5500 tokens]'),
    ],
    "context7_calls": [
        ('context7.query-docs(libraryId="/django/django", query="QuerySet filter signature usage example")',
         '### QuerySet.filter(*args, **kwargs)\nReturns a new QuerySet containing objects that match the given lookup parameters.\n```APIDOC\n## METHOD QuerySet.filter(*args, **kwargs)\nReturns a new QuerySet instance with filtered results. Multiple kwargs joined via AND.\nRequest Example:\n```python\nEntry.objects.filter(pub_date__year=2005, headline__contains="Hello")\n```\n```\n--------------------------------\n### Case Expression - Filter Usage\n```python\nClient.objects.filter(\n    registered_on__lte=Case(\n        When(account_type=Client.GOLD, then=a_month_ago),\n        When(account_type=Client.PLATINUM, then=a_year_ago),\n    ),\n)\n```\n[3 more snippets: Exists, F() filters, basic filter usage]'),
    ],
}

# ============== EFCORE ==============
# Task: "Understand DbContext.OnConfiguring — signature, body, real callers"
EFCORE = {
    "xmp4_calls": [
        ('xmp4_info(project="efcore/EFCore", symbol_name="DbContext", file_path="src/EFCore/DbContext.cs")',
         'Type DbContext src/EFCore/DbContext.cs:49\n[docs available: call with docs=summary|full]'),
        ('xmp4_source(project="efcore/EFCore", symbol_name="OnConfiguring", file_path="src/EFCore/DbContext.cs")',
         'Method OnConfiguring src/EFCore/DbContext.cs:519\n    /// <param name="optionsBuilder">\n    ///     A builder used to create or modify options for this context.\n    /// </param>\n    protected internal virtual void OnConfiguring(DbContextOptionsBuilder optionsBuilder)\n    {\n    }'),
        ('xmp4_callers(project="efcore/EFCore", symbol_name="OnConfiguring", file_path="src/EFCore/DbContext.cs", page_size=10)',
         '3 callers found (page 1/1)\nFinder src/EFCore/DbContext.cs:391\nOnConfiguring test/EFCore.Tests/DbContextTest.cs:505\nOnConfiguring test/EFCore.Cosmos.FunctionalTests/ReloadTest.cs:83'),
    ],
    "grep_clone_cost": ('git clone --depth=1 https://github.com/dotnet/efcore.git',
                       'Cloning into efcore... Receiving objects: 100%, 125 MiB in 60s'),
    "grep_repo": "dotnet-efcore",
    "grep_cmds": [
        ('grep -rn "class DbContext" --include="*.cs" . | head -10',
         ["bash", "-c", 'grep -rn "class DbContext" --include="*.cs" . | head -10']),
        ('grep -rn "OnConfiguring" --include="*.cs" . | head -20',
         ["bash", "-c", 'grep -rn "OnConfiguring" --include="*.cs" . | head -20']),
    ],
    "gitmcp_calls": [
        ('gitmcp-efcore.search_efcore_code(query="DbContext OnConfiguring")',
         '### Code Search Results for: "DbContext OnConfiguring"\n\nFound 169 matches in dotnet/efcore. Page 1 of 6.\n\n#### DbContext.cs\n- Path: src/EFCore/DbContext.cs\n- URL: https://github.com/dotnet/efcore/blob/.../DbContext.cs\n[29 more file entries ~170 tok each, total ~5100 tokens]'),
    ],
    "context7_calls": [
        ('context7.query-docs(libraryId="/dotnet/efcore", query="DbContext OnConfiguring override pattern")',
         '### Configure SQL Server Provider in EF Core\n```csharp\npublic class MyDbContext : DbContext\n{\n    protected override void OnConfiguring(DbContextOptionsBuilder options)\n        => options.UseSqlServer("Data Source=(localdb)\\MSSQLLocalDB;Initial Catalog=MyDatabase");\n    public DbSet<Customer> Customers { get; set; }\n}\n```\n--------------------------------\n### Configure In-Memory Database\n```csharp\nprotected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)\n{\n    optionsBuilder.UseInMemoryDatabase("MyDatabase");\n}\n```\n[3 more snippets: SQLite, SqlServer, DbContextOptionsBuilder]'),
    ],
}


REPO_BLOCKS = {
    "spring-boot": SPRING,
    "tokio":       TOKIO,
    "django":      DJANGO,
    "efcore":      EFCORE,
}


def sum_tokens(pairs):
    """Given list of (request_str, response_str), return (Σ request, Σ response, Σ total, call_count)."""
    r = sum(tok(rq) for rq, _ in pairs)
    o = sum(tok(rs) for _, rs in pairs)
    return r, o, r + o, len(pairs)


def run_grep(repo_subdir, cmds):
    """Run grep commands in the local clone; return (total output tokens, exit codes)."""
    cwd = REPOS / repo_subdir
    if not cwd.exists():
        return 0, [(c[0], "repo_not_found") for c in cmds]
    out_parts = []
    codes = []
    for emit_str, shell in cmds:
        try:
            r = subprocess.run(shell, cwd=cwd, capture_output=True, text=True, timeout=120)
            out_parts.append(r.stdout)
            codes.append((emit_str, r.returncode))
        except subprocess.TimeoutExpired:
            out_parts.append("TIMEOUT")
            codes.append((emit_str, "TIMEOUT"))
    total_output = "\n".join(out_parts)
    return tok(total_output), codes


def analyze_repo(name, block):
    # xmp4
    x_req, x_out, x_tot, x_n = sum_tokens(block["xmp4_calls"])

    # grep: count clone cost (request + output tokens) + grep calls
    clone_req_tok = tok(block["grep_clone_cost"][0])
    clone_out_tok = tok(block["grep_clone_cost"][1])
    grep_req_tok = sum(tok(c[0]) for c in block["grep_cmds"])
    grep_out_tok, grep_codes = run_grep(block["grep_repo"], block["grep_cmds"])
    g_req = clone_req_tok + grep_req_tok
    g_out = clone_out_tok + grep_out_tok
    g_tot = g_req + g_out
    g_n = 1 + len(block["grep_cmds"])  # clone + grep calls

    # GitMCP
    gm_req, gm_out, gm_tot, gm_n = sum_tokens(block["gitmcp_calls"])

    # Context7
    c7_req, c7_out, c7_tot, c7_n = sum_tokens(block["context7_calls"])

    return {
        "repo": name,
        "xmp4_calls": x_n, "xmp4_req": x_req, "xmp4_out": x_out, "xmp4_total": x_tot,
        "grep_calls": g_n, "grep_req": g_req, "grep_out": g_out, "grep_total": g_tot,
        "gitmcp_calls": gm_n, "gitmcp_req": gm_req, "gitmcp_out": gm_out, "gitmcp_total": gm_tot,
        "c7_calls": c7_n, "c7_req": c7_req, "c7_out": c7_out, "c7_total": c7_tot,
    }


def main():
    rows = [analyze_repo(n, b) for n, b in REPO_BLOCKS.items()]

    # CSV
    out_csv = Path(__file__).parent / "results" / "2026-04-20-bigrepo-4backend.csv"
    out_csv.parent.mkdir(exist_ok=True, parents=True)
    with out_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # Console summary
    print(f"{'repo':<12}{'xmp4':>10}{'grep':>10}{'gitmcp':>10}{'ctx7':>10}  {'xmp4/grep':>10}{'xmp4/gm':>10}{'xmp4/c7':>10}")
    print("-" * 92)
    for r in rows:
        print(f"{r['repo']:<12}"
              f"{r['xmp4_total']:>10}{r['grep_total']:>10}{r['gitmcp_total']:>10}{r['c7_total']:>10}  "
              f"{r['grep_total']/r['xmp4_total']:>9.1f}x"
              f"{r['gitmcp_total']/r['xmp4_total']:>9.1f}x"
              f"{r['c7_total']/r['xmp4_total']:>9.1f}x")
    print("-" * 92)

    Σx = sum(r["xmp4_total"] for r in rows)
    Σg = sum(r["grep_total"] for r in rows)
    Σgm = sum(r["gitmcp_total"] for r in rows)
    Σc = sum(r["c7_total"] for r in rows)
    Σxn = sum(r["xmp4_calls"] for r in rows)
    Σgn = sum(r["grep_calls"] for r in rows)
    Σgmn = sum(r["gitmcp_calls"] for r in rows)
    Σcn = sum(r["c7_calls"] for r in rows)
    print(f"{'TOTAL':<12}{Σx:>10}{Σg:>10}{Σgm:>10}{Σc:>10}  "
          f"{Σg/Σx:>9.1f}x{Σgm/Σx:>9.1f}x{Σc/Σx:>9.1f}x")
    print(f"{'calls':<12}{Σxn:>10}{Σgn:>10}{Σgmn:>10}{Σcn:>10}")

    # % savings vs each
    print(f"\nxmp4 vs grep:   {(1-Σx/Σg)*100:.1f}% saving")
    print(f"xmp4 vs gitmcp: {(1-Σx/Σgm)*100:.1f}% saving")
    print(f"xmp4 vs ctx7:   {(1-Σx/Σc)*100:.1f}% saving")
    print(f"\nCSV: {out_csv}")


if __name__ == "__main__":
    main()
