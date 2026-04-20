#!/usr/bin/env python3
"""
xmp4 vs grep — pilot benchmark (12 cells, 6 tier-1 languages).

xmp4 outputs captured verbatim on 2026-04-20 against mcp.example4.ai v1.1.3.
grep outputs generated here via subprocess against local clones in
/mnt/f/lsai-testing/repos/.

Tokenization: tiktoken cl100k_base (OpenAI GPT-4). Same tokenizer for every
backend — ratios are fair. Absolute token counts would shift with Anthropic
tokenizer but the xmp4-vs-grep ratio is essentially unchanged.

Usage:
    python3 run_pilot.py
"""

import csv
import subprocess
import tiktoken
from pathlib import Path

ENC = tiktoken.get_encoding("cl100k_base")
REPOS_ROOT = Path("/mnt/f/lsai-testing/repos")


def tok(s: str) -> int:
    return len(ENC.encode(s))


# --- xmp4 outputs captured live on 2026-04-20 against mcp.example4.ai v1.1.3 ---
# Each entry: (args_emitted_by_model, response_body)
XMP4 = {
    # Task 1: find symbol definition
    "thiserror_info": (
        'xmp4_info(project="thiserror/thiserror", symbol_name="TupleError", file_path="tests/test_error.rs")',
        "Struct TupleError tests/test_error.rs:24",
    ),
    "scrutor_info": (
        'xmp4_info(project="Scrutor/Scrutor", symbol_name="ServiceCollectionExtensions", file_path="src/Scrutor/ServiceCollectionExtensions.cs")',
        "Type ServiceCollectionExtensions src/Scrutor/ServiceCollectionExtensions.cs:7\n[docs available: call with docs=summary|full]",
    ),
    "orjson_info": (
        'xmp4_info(project="orjson/orjson", symbol_name="loads", file_path="src/lib.rs")',
        "Function loads src/lib.rs:229",
    ),
    "slf4j_info": (
        'xmp4_info(project="slf4j/slf4j-bom", symbol_name="AbstractLogger", file_path="slf4j-api/src/main/java/org/slf4j/helpers/AbstractLogger.java")',
        "Class AbstractLogger slf4j-api/src/main/java/org/slf4j/helpers/AbstractLogger.java:42\n[docs available: call with docs=summary|full]",
    ),
    "zustand_info": (
        'xmp4_info(project="zustand/zustand", symbol_name="create", file_path="src/react.ts")',
        "Member create src/react.ts:63\n[docs available: call with docs=summary|full]",
    ),
    "cron_info": (
        'xmp4_info(project="cron-expression/cron-expression", symbol_name="CronExpression", file_path="src/Cron/CronExpression.php")',
        "Type CronExpression src/Cron/CronExpression.php:28\n[docs available: call with docs=summary|full]",
    ),
    # Task 2: find all usages
    "thiserror_usages": (
        'xmp4_usages(project="thiserror/thiserror", symbol_name="TupleError", file_path="tests/test_error.rs", page_size=20)',
        "2 usages found (page 1/1)\ntests/test_error.rs:24,52",
    ),
    "scrutor_usages": (
        'xmp4_usages(project="Scrutor/Scrutor", symbol_name="ServiceCollectionExtensions", file_path="src/Scrutor/ServiceCollectionExtensions.cs", page_size=20)',
        "1 usage found (page 1/1)\nsrc/Scrutor/ServiceCollectionExtensions.cs:7",
    ),
    "orjson_usages": (
        'xmp4_usages(project="orjson/orjson", symbol_name="loads", file_path="src/lib.rs", page_size=20)',
        "2 usages found (page 1/1)\nsrc/lib.rs:137,229",
    ),
    "slf4j_usages": (
        'xmp4_usages(project="slf4j/slf4j-bom", symbol_name="AbstractLogger", file_path="slf4j-api/src/main/java/org/slf4j/helpers/AbstractLogger.java", page_size=20)',
        "2 usages found (page 1/1)\nslf4j-api/src/main/java/org/slf4j/helpers/AbstractLogger.java:42\nslf4j-api/src/main/java/org/slf4j/helpers/LegacyAbstractLogger.java:10",
    ),
    "zustand_usages": (
        'xmp4_usages(project="zustand/zustand", symbol_name="create", file_path="src/react.ts", page_size=20)',
        "109 usages found (page 1/6)\nsrc/react.ts:63\ntests/basic.test.tsx:12,24,51,72,132,167,195,326,426,443,460,471,569,615,661,705,731\ntests/middlewareTypes.test.tsx:2,42",
    ),
    "cron_usages": (
        'xmp4_usages(project="cron-expression/cron-expression", symbol_name="CronExpression", file_path="src/Cron/CronExpression.php", page_size=20)',
        "39 usages found (page 1/2)\nsrc/Cron/CronExpression.php:68,69,70,71,72,73,79,90,100,104,115,119,123,133,144,150,153,166,184,199",
    ),
}

# --- grep baseline setup ---
# Each entry: (local_dir, command_to_emit, shell_cmd_list)
GREP = [
    # Task 1: find symbol definition — realistic AI-agent grep for the definition
    ("thiserror_info", "github.com-dtolnay-thiserror", 'grep -rn "struct TupleError" .', ["grep", "-rn", "struct TupleError", "."]),
    ("scrutor_info", "github.com-khellang-scrutor", 'grep -rn "class ServiceCollectionExtensions" .', ["grep", "-rn", "class ServiceCollectionExtensions", "."]),
    ("orjson_info", "github.com-ijl-orjson", 'grep -rn "fn loads" .', ["grep", "-rn", "fn loads", "."]),
    ("slf4j_info", "github.com-qos-ch-slf4j", 'grep -rn "class AbstractLogger" .', ["grep", "-rn", "class AbstractLogger", "."]),
    ("zustand_info", "github.com-pmndrs-zustand", 'grep -rn "export.*create" src/', ["grep", "-rn", "export.*create", "src/"]),
    ("cron_info", "github.com-dragonmantank-cron-expression", 'grep -rn "class CronExpression" .', ["grep", "-rn", "class CronExpression", "."]),
    # Task 2: find all usages — naive grep for the symbol name
    ("thiserror_usages", "github.com-dtolnay-thiserror", 'grep -rn "TupleError" .', ["grep", "-rn", "TupleError", "."]),
    ("scrutor_usages", "github.com-khellang-scrutor", 'grep -rn "ServiceCollectionExtensions" .', ["grep", "-rn", "ServiceCollectionExtensions", "."]),
    ("orjson_usages", "github.com-ijl-orjson", 'grep -rn "loads" .', ["grep", "-rn", "loads", "."]),
    ("slf4j_usages", "github.com-qos-ch-slf4j", 'grep -rn "AbstractLogger" .', ["grep", "-rn", "AbstractLogger", "."]),
    ("zustand_usages", "github.com-pmndrs-zustand", 'grep -rn "create" src/ tests/', ["grep", "-rn", "create", "src/", "tests/"]),
    ("cron_usages", "github.com-dragonmantank-cron-expression", 'grep -rn "CronExpression" .', ["grep", "-rn", "CronExpression", "."]),
]

# Human-readable labels for the report
LABELS = {
    "thiserror_info": ("thiserror", "Rust", "find class", "TupleError"),
    "scrutor_info": ("Scrutor", "C#", "find class", "ServiceCollectionExtensions"),
    "orjson_info": ("orjson", "Python", "find fn", "loads"),
    "slf4j_info": ("slf4j", "Java", "find class", "AbstractLogger"),
    "zustand_info": ("zustand", "TypeScript", "find fn", "create"),
    "cron_info": ("cron-expression", "PHP", "find class", "CronExpression"),
    "thiserror_usages": ("thiserror", "Rust", "usages", "TupleError"),
    "scrutor_usages": ("Scrutor", "C#", "usages", "ServiceCollectionExtensions"),
    "orjson_usages": ("orjson", "Python", "usages", "loads"),
    "slf4j_usages": ("slf4j", "Java", "usages", "AbstractLogger"),
    "zustand_usages": ("zustand", "TypeScript", "usages", "create"),
    "cron_usages": ("cron-expression", "PHP", "usages", "CronExpression"),
}


def run_grep(repo_dir: str, cmd: list[str]) -> tuple[str, int]:
    """Run grep in the repo dir, capture stdout, return (output, exit_code)."""
    path = REPOS_ROOT / repo_dir
    if not path.exists():
        return (f"ERROR: repo not found at {path}", 2)
    try:
        r = subprocess.run(cmd, cwd=path, capture_output=True, text=True, timeout=60)
        return (r.stdout, r.returncode)
    except subprocess.TimeoutExpired:
        return ("ERROR: grep timed out after 60s", 3)


def main():
    rows = []
    for key in XMP4:
        x_args, x_body = XMP4[key]
        x_in = tok(x_args)
        x_out = tok(x_body)
        x_total = x_in + x_out

        g_entry = next(g for g in GREP if g[0] == key)
        _, repo_dir, g_args, g_cmd = g_entry
        g_body, rc = run_grep(repo_dir, g_cmd)
        g_in = tok(g_args)
        g_out = tok(g_body)
        g_total = g_in + g_out

        savings = 1.0 - (x_total / g_total) if g_total > 0 else 0.0
        repo_name, lang, task, sym = LABELS[key]

        rows.append({
            "cell_id": key,
            "repo": repo_name,
            "lang": lang,
            "task": task,
            "symbol": sym,
            "xmp4_in_tok": x_in,
            "xmp4_out_tok": x_out,
            "xmp4_total_tok": x_total,
            "grep_in_tok": g_in,
            "grep_out_tok": g_out,
            "grep_total_tok": g_total,
            "grep_exit": rc,
            "savings_pct": round(savings * 100, 1),
            "ratio_grep_over_xmp4": round(g_total / x_total, 1) if x_total > 0 else None,
        })

    # CSV output
    out_csv = Path(__file__).parent / "results" / "2026-04-20-pilot.csv"
    out_csv.parent.mkdir(exist_ok=True, parents=True)
    with out_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # Stdout summary
    print(f"{'cell':<22} {'lang':<12} {'task':<12} {'xmp4':>6} {'grep':>8} {'saving':>8} {'ratio':>6}")
    for r in rows:
        print(f"{r['cell_id']:<22} {r['lang']:<12} {r['task']:<12} "
              f"{r['xmp4_total_tok']:>6} {r['grep_total_tok']:>8} "
              f"{r['savings_pct']:>7.1f}% {r['ratio_grep_over_xmp4']:>5}x")

    # Aggregate stats
    x_sum = sum(r["xmp4_total_tok"] for r in rows)
    g_sum = sum(r["grep_total_tok"] for r in rows)
    overall = 1.0 - (x_sum / g_sum)
    print(f"\nTOTAL: xmp4={x_sum}  grep={g_sum}  saving={overall*100:.1f}%  ratio={g_sum/x_sum:.1f}x")

    # Split by task type
    for tname in ("find class", "find fn", "usages"):
        subset = [r for r in rows if r["task"] == tname]
        if not subset: continue
        xs = sum(r["xmp4_total_tok"] for r in subset)
        gs = sum(r["grep_total_tok"] for r in subset)
        pct = 1.0 - xs / gs if gs > 0 else 0
        print(f"  {tname:<14}: xmp4={xs}  grep={gs}  saving={pct*100:.1f}%  ({len(subset)} cells)")

    print(f"\nCSV written to: {out_csv}")


if __name__ == "__main__":
    main()
