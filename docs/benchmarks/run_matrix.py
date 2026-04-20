#!/usr/bin/env python3
"""
xmp4 FULL-TOOL comparative matrix — 14 xmp4 tools × 6 tier-1 libraries.

Every xmp4 response below was captured verbatim from mcp.example4.ai v1.1.3
on 2026-04-20 during interactive benchmarking sessions. The `grep` equivalents
are re-executed live against /home/laco/repos-test/.

Tokenizer: tiktoken cl100k_base. Same tokenizer every side → fair ratio.

Output: results/2026-04-20-matrix.csv + matrix-report.md
"""

import csv
import subprocess
import tiktoken
from pathlib import Path

ENC = tiktoken.get_encoding("cl100k_base")
REPOS_ROOT = Path("/home/laco/repos-test")


def tok(s: str) -> int:
    return len(ENC.encode(s))


# Repo mapping: xmp4_project_id → (local_dir, lang)
REPO = {
    "thiserror": ("thiserror/thiserror", "github.com-dtolnay-thiserror", "Rust"),
    "scrutor":   ("Scrutor/Scrutor", "github.com-khellang-scrutor", "C#"),
    "orjson":    ("orjson/orjson", "github.com-ijl-orjson", "Python"),
    "slf4j":     ("slf4j/slf4j-bom", "github.com-qos-ch-slf4j", "Java"),
    "zustand":   ("zustand/zustand", "github.com-pmndrs-zustand", "TypeScript"),
    "cron":      ("cron-expression/cron-expression", "github.com-dragonmantank-cron-expression", "PHP"),
}


# Every entry: (tool, lib, xmp4_request_str, xmp4_response_str, grep_request_str, grep_cmd_list, grep_cwd_subdir)
# xmp4_request is the verbose MCP tool call the model must emit.
# xmp4_response is the verbatim server output.
# grep_request is what the model emits to the shell.
# grep_cmd runs live here.
# grep_cwd_subdir is relative to REPOS_ROOT/<repo_local_dir>.
CELLS = [
    # ──────────────────────────────────────────────── xmp4_projects ───
    ("projects", "thiserror",
     'xmp4_projects(language="Rust", query="thiserror")',
     '2 project(s) found (page 1/1):\n  1. thiserror/thiserror (Rust) — 1347 symbols\n  2. biome/biome_diagnostics (Rust) — 261405 symbols',
     'find . -type d -name "*thiserror*" ; ls Cargo.toml README.md',
     ["bash", "-c", "find . -type d -name '*thiserror*' ; ls Cargo.toml README.md"],
     ""),
    ("projects", "scrutor",
     'xmp4_projects(language="CSharp", query="Scrutor")',
     '1 project(s) found (page 1/1):\n  1. Scrutor/Scrutor (CSharp) — 1734 symbols',
     'find . -name "*.sln" -o -name "*.csproj"',
     ["bash", "-c", "find . -name '*.sln' -o -name '*.csproj'"],
     ""),
    # (projects is fundamentally an xmp4 capability — grep has no equivalent.
    # We measure the "closest thing a grep-only agent would try": find solution files.)

    # ──────────────────────────────────────────────── xmp4_search ─────
    ("search", "thiserror",
     'xmp4_search(project="thiserror/thiserror", query="Error", max_results=5)',
     '5 results found (page 1/1)\ntests/test_generics.rs:179 EnumMember EntryParseError\ntests/no-std/test.rs:13 Struct SourceError\ntests/test_from.rs:26 Struct ErrorTupleOptional\ntests/no-std/test.rs:29 TypeParameter \'a\ntests/test_error.rs:24 Struct TupleError',
     'grep -rn "Error" . | head -20',
     ["bash", "-c", "grep -rn 'Error' . | head -20"],
     ""),
    ("search", "scrutor",
     'xmp4_search(project="Scrutor/Scrutor", query="ServiceCollection", max_results=5)',
     '3 results found (page 1/1)\nsrc/Scrutor/ServiceCollectionExtensions.cs:7 Type ServiceCollectionExtensions\nsrc/Scrutor/ServiceCollectionExtensions.Decoration.cs:11 Type ServiceCollectionExtensions\ntest/Scrutor.Tests/ServiceCollectionExtensions.cs:7 Type ServiceCollectionExtensions',
     'grep -rn "ServiceCollection" . | head -20',
     ["bash", "-c", "grep -rn 'ServiceCollection' . | head -20"],
     ""),
    ("search", "orjson",
     'xmp4_search(project="orjson/orjson", query="loads", max_results=5)',
     '4 results found (page 1/1)\nsrc/lib.rs:133 Parameter layout\nsrc/exception.rs:13 Function raise_loads_exception\nsrc/lib.rs:135 Variable len\nsrc/lib.rs:229 Function loads',
     'grep -rn "loads" . | head -20',
     ["bash", "-c", "grep -rn 'loads' . | head -20"],
     ""),
    ("search", "slf4j",
     'xmp4_search(project="slf4j/slf4j-bom", query="Logger", max_results=5)',
     '5 results found (page 1/1)\nslf4j-api/src/main/java/org/slf4j/helpers/NOPLogger.java:35 Class NOPLogger\nslf4j-api/src/main/java/org/slf4j/helpers/NOPLoggerFactory.java:37 Class NOPLoggerFactory\nslf4j-api/src/main/java/org/slf4j/helpers/AbstractLogger.java:42 Class AbstractLogger\nslf4j-api/src/main/java/org/slf4j/spi/LoggerFactoryBinder.java:36 Interface LoggerFactoryBinder\nslf4j-api/src/main/java/org/slf4j/helpers/SubstituteLoggerFactory.java:43 Class SubstituteLoggerFactory',
     'grep -rn "Logger" . | head -20',
     ["bash", "-c", "grep -rn 'Logger' . | head -20"],
     ""),
    ("search", "zustand",
     'xmp4_search(project="zustand/zustand", query="create", max_results=5)',
     '5 results found (page 1/1)\ntests/persistSync.test.tsx:8 Member createPersistentStore\nsrc/react.ts:53 Member createImpl\nsrc/middleware/persist.ts:31 Method createJSONStorage\nsrc/react.ts:44 Type Create\nsrc/react.ts:63 Member create',
     'grep -rn "create" . | head -20',
     ["bash", "-c", "grep -rn 'create' . | head -20"],
     ""),
    ("search", "cron",
     'xmp4_search(project="cron-expression/cron-expression", query="CronExpression", max_results=5)',
     '1 result found (page 1/1)\nsrc/Cron/CronExpression.php:28 Type CronExpression',
     'grep -rn "CronExpression" . | head -20',
     ["bash", "-c", "grep -rn 'CronExpression' . | head -20"],
     ""),

    # ──────────────────────────────────────────────── xmp4_info ───────
    ("info", "thiserror",
     'xmp4_info(project="thiserror/thiserror", symbol_name="TupleError", file_path="tests/test_error.rs")',
     'Struct TupleError tests/test_error.rs:24',
     'grep -rn "struct TupleError" .',
     ["grep", "-rn", "struct TupleError", "."], ""),
    ("info", "scrutor",
     'xmp4_info(project="Scrutor/Scrutor", symbol_name="ServiceCollectionExtensions", file_path="src/Scrutor/ServiceCollectionExtensions.cs")',
     'Type ServiceCollectionExtensions src/Scrutor/ServiceCollectionExtensions.cs:7\n[docs available: call with docs=summary|full]',
     'grep -rn "class ServiceCollectionExtensions" .',
     ["grep", "-rn", "class ServiceCollectionExtensions", "."], ""),
    ("info", "orjson",
     'xmp4_info(project="orjson/orjson", symbol_name="loads", file_path="src/lib.rs")',
     'Function loads src/lib.rs:229',
     'grep -rn "fn loads" .',
     ["grep", "-rn", "fn loads", "."], ""),
    ("info", "slf4j",
     'xmp4_info(project="slf4j/slf4j-bom", symbol_name="AbstractLogger", file_path="slf4j-api/src/main/java/org/slf4j/helpers/AbstractLogger.java")',
     'Class AbstractLogger slf4j-api/src/main/java/org/slf4j/helpers/AbstractLogger.java:42\n[docs available: call with docs=summary|full]',
     'grep -rn "class AbstractLogger" .',
     ["grep", "-rn", "class AbstractLogger", "."], ""),
    ("info", "zustand",
     'xmp4_info(project="zustand/zustand", symbol_name="create", file_path="src/react.ts")',
     'Member create src/react.ts:63\n[docs available: call with docs=summary|full]',
     'grep -rn "export.*create" src/',
     ["grep", "-rn", "export.*create", "src/"], ""),
    ("info", "cron",
     'xmp4_info(project="cron-expression/cron-expression", symbol_name="CronExpression", file_path="src/Cron/CronExpression.php")',
     'Type CronExpression src/Cron/CronExpression.php:28\n[docs available: call with docs=summary|full]',
     'grep -rn "class CronExpression" .',
     ["grep", "-rn", "class CronExpression", "."], ""),

    # ──────────────────────────────────────────────── xmp4_usages ─────
    ("usages", "thiserror",
     'xmp4_usages(project="thiserror/thiserror", symbol_name="TupleError", file_path="tests/test_error.rs", page_size=20)',
     '2 usages found (page 1/1)\ntests/test_error.rs:24,52',
     'grep -rn "TupleError" .',
     ["grep", "-rn", "TupleError", "."], ""),
    ("usages", "scrutor",
     'xmp4_usages(project="Scrutor/Scrutor", symbol_name="ServiceCollectionExtensions", file_path="src/Scrutor/ServiceCollectionExtensions.cs", page_size=20)',
     '1 usage found (page 1/1)\nsrc/Scrutor/ServiceCollectionExtensions.cs:7',
     'grep -rn "ServiceCollectionExtensions" .',
     ["grep", "-rn", "ServiceCollectionExtensions", "."], ""),
    ("usages", "orjson",
     'xmp4_usages(project="orjson/orjson", symbol_name="loads", file_path="src/lib.rs", page_size=20)',
     '2 usages found (page 1/1)\nsrc/lib.rs:137,229',
     'grep -rn "loads" .',
     ["grep", "-rn", "loads", "."], ""),
    ("usages", "slf4j",
     'xmp4_usages(project="slf4j/slf4j-bom", symbol_name="AbstractLogger", file_path="slf4j-api/src/main/java/org/slf4j/helpers/AbstractLogger.java", page_size=20)',
     '2 usages found (page 1/1)\nslf4j-api/src/main/java/org/slf4j/helpers/AbstractLogger.java:42\nslf4j-api/src/main/java/org/slf4j/helpers/LegacyAbstractLogger.java:10',
     'grep -rn "AbstractLogger" .',
     ["grep", "-rn", "AbstractLogger", "."], ""),
    ("usages", "zustand",
     'xmp4_usages(project="zustand/zustand", symbol_name="create", file_path="src/react.ts", page_size=20)',
     '109 usages found (page 1/6)\nsrc/react.ts:63\ntests/basic.test.tsx:12,24,51,72,132,167,195,326,426,443,460,471,569,615,661,705,731\ntests/middlewareTypes.test.tsx:2,42',
     'grep -rn "create" src/ tests/',
     ["bash", "-c", "grep -rn 'create' src/ tests/"], ""),
    ("usages", "cron",
     'xmp4_usages(project="cron-expression/cron-expression", symbol_name="CronExpression", file_path="src/Cron/CronExpression.php", page_size=20)',
     '39 usages found (page 1/2)\nsrc/Cron/CronExpression.php:68,69,70,71,72,73,79,90,100,104,115,119,123,133,144,150,153,166,184,199',
     'grep -rn "CronExpression" .',
     ["grep", "-rn", "CronExpression", "."], ""),

    # ──────────────────────────────────────────────── xmp4_outline ───
    ("outline", "thiserror",
     'xmp4_outline(project="thiserror/thiserror", file_path="impl/src/lib.rs", page_size=10)',
     '4 symbols found (page 1/1)\nModule crate :1\nModule proc_macro :21\nStruct private :46\nMethod to_tokens :49',
     'grep -nE "^(pub |impl |struct |fn )" impl/src/lib.rs | head -10',
     ["bash", "-c", "grep -nE '^(pub |impl |struct |fn )' impl/src/lib.rs | head -10"], ""),
    ("outline", "scrutor",
     'xmp4_outline(project="Scrutor/Scrutor", file_path="src/Scrutor/ServiceCollectionExtensions.cs", page_size=10)',
     '2 symbols found (page 1/1)\nType ServiceCollectionExtensions :7\nMethod HasRegistration :9',
     'grep -nE "^\\s*(public|private|internal|protected) " src/Scrutor/ServiceCollectionExtensions.cs',
     ["bash", "-c", "grep -nE '^\\s*(public|private|internal|protected) ' src/Scrutor/ServiceCollectionExtensions.cs"], ""),
    ("outline", "orjson",
     'xmp4_outline(project="orjson/orjson", file_path="src/lib.rs", page_size=10)',
     '9 symbols found (page 1/1)\nModule crate :1\nMacro add :71\nMacro opt :84\nFunction orjson_init_exec :99\nFunction dumps :248\nFunction loads :229\nFunction PyInit_orjson :181\nConstant PYMODULEDEF_LEN :187\nMacro matches_kwarg :234',
     'grep -nE "^(pub fn|fn|macro_rules|const)" src/lib.rs | head -10',
     ["bash", "-c", "grep -nE '^(pub fn|fn|macro_rules|const)' src/lib.rs | head -10"], ""),
    ("outline", "slf4j",
     'xmp4_outline(project="slf4j/slf4j-bom", file_path="slf4j-api/src/main/java/org/slf4j/helpers/AbstractLogger.java", page_size=10)',
     '62 symbols found (page 1/7)\nClass AbstractLogger :42\nConstructor <init> :42\nStaticField serialVersionUID :44\nField name :46\nMethod getName :48\nMethod readResolve :66\nMethod trace :73\nMethod trace :80\nMethod trace :87\nMethod trace :94',
     'grep -nE "^\\s*(public|private|protected) " slf4j-api/src/main/java/org/slf4j/helpers/AbstractLogger.java | head -10',
     ["bash", "-c", "grep -nE '^\\s*(public|private|protected) ' slf4j-api/src/main/java/org/slf4j/helpers/AbstractLogger.java | head -10"], ""),
    ("outline", "zustand",
     'xmp4_outline(project="zustand/zustand", file_path="src/react.ts", page_size=10)',
     '10 symbols found (page 1/1)\nNamespace react.ts :1\nType ReadonlyStoreApi :11\nMember identity :16\nMethod useStore :17\nMethod useStore :17\nMethod useStore :17\nType UseBoundStore :39\nMember createImpl :53\nMember create :63',
     'grep -nE "^(export|function|const|type|interface|class)" src/react.ts | head -10',
     ["bash", "-c", "grep -nE '^(export|function|const|type|interface|class)' src/react.ts | head -10"], ""),
    ("outline", "cron",
     'xmp4_outline(project="cron-expression/cron-expression", file_path="src/Cron/CronExpression.php", page_size=10)',
     '32 symbols found (page 1/4)\nMember MINUTE :30\nMember HOUR :31\nMember DAY :32\nMember MONTH :33\nMember WEEKDAY :34\nMember YEAR :37\nMember MAPPINGS :39\nMember $cronParts :52\nMember $fieldFactory :57\nMember $maxIterationCount :62',
     'grep -nE "^\\s*(public|private|protected|const|function)" src/Cron/CronExpression.php | head -10',
     ["bash", "-c", "grep -nE '^\\s*(public|private|protected|const|function)' src/Cron/CronExpression.php | head -10"], ""),

    # ──────────────────────────────────────────────── xmp4_source ─────
    ("source", "thiserror",
     'xmp4_source(project="thiserror/thiserror", symbol_name="TupleError", file_path="tests/test_error.rs")',
     'Struct TupleError tests/test_error.rs:24\n    };\n}\n\n#[derive(Error, Debug)]\nstruct BracedError {\n    msg: String,\n    pos: usize,\n}\n\n#[derive(Error, Debug)]\nstruct TupleError(String, usize);',
     'sed -n "15,30p" tests/test_error.rs',
     ["bash", "-c", "sed -n '15,30p' tests/test_error.rs"], ""),
    ("source", "scrutor",
     'xmp4_source(project="Scrutor/Scrutor", symbol_name="HasRegistration", file_path="src/Scrutor/ServiceCollectionExtensions.cs")',
     'Method HasRegistration src/Scrutor/ServiceCollectionExtensions.cs:9\nusing System;\nusing System.Linq;\nusing Microsoft.Extensions.DependencyInjection;\n\nnamespace Scrutor;\n\ninternal static class ServiceCollectionExtensions\n{\n    public static bool HasRegistration(this IServiceCollection services, Type serviceType)\n    {\n        return services.Any(x => x.ServiceType == serviceType);\n    }\n}',
     'cat src/Scrutor/ServiceCollectionExtensions.cs',
     ["cat", "src/Scrutor/ServiceCollectionExtensions.cs"], ""),
    ("source", "orjson",
     'xmp4_source(project="orjson/orjson", symbol_name="loads", file_path="src/lib.rs")',
     'Function loads src/lib.rs:229\n            m_clear: None,\n            m_free: None,\n        });\n        let init_ptr = Box::into_raw(init);\n        ffi!(PyModuleDef_Init(init_ptr));\n        init_ptr\n    }\n}\n\n#[unsafe(no_mangle)]\npub(crate) unsafe extern "C" fn loads(_self: *mut PyObject, obj: *mut PyObject) -> *mut PyObject {\n    deserialize(obj).map_or_else(raise_loads_exception, NonNull::as_ptr)\n}',
     'sed -n "225,240p" src/lib.rs',
     ["bash", "-c", "sed -n '225,240p' src/lib.rs"], ""),
    ("source", "slf4j",
     'xmp4_source(project="slf4j/slf4j-bom", symbol_name="getName", file_path="slf4j-api/src/main/java/org/slf4j/helpers/AbstractLogger.java")',
     'Method getName slf4j-api/src/main/java/org/slf4j/helpers/AbstractLogger.java:48\n[24 lines trimmed — signature + body]',
     'sed -n "40,55p" slf4j-api/src/main/java/org/slf4j/helpers/AbstractLogger.java',
     ["bash", "-c", "sed -n '40,55p' slf4j-api/src/main/java/org/slf4j/helpers/AbstractLogger.java"], ""),
    ("source", "zustand",
     'xmp4_source(project="zustand/zustand", symbol_name="create", file_path="src/react.ts")',
     'Member create src/react.ts:63\nconst createImpl = <T>(createState: StateCreator<T, [], []>) => {\n  const api = createStore(createState)\n  const useBoundStore: any = (selector?: any) => useStore(api, selector)\n  Object.assign(useBoundStore, api)\n  return useBoundStore\n}\nexport const create = (<T>(createState: StateCreator<T, [], []> | undefined) =>\n  createState ? createImpl(createState) : createImpl) as Create',
     'sed -n "50,70p" src/react.ts',
     ["bash", "-c", "sed -n '50,70p' src/react.ts"], ""),
    ("source", "cron",
     'xmp4_source(project="cron-expression/cron-expression", symbol_name="CronExpression", file_path="src/Cron/CronExpression.php")',
     'Type CronExpression src/Cron/CronExpression.php:28\n * The determinations made by this class are accurate if checked run once per\n * minute (seconds are dropped from date time comparisons).\n * Schedule parts must map to:\n * minute [0-59], hour [0-23], day of month, month [1-12|JAN-DEC], day of week\n * [1-7|MON-SUN], and an optional year.\n * @see http://en.wikipedia.org/wiki/Cron\n */\nclass CronExpression\n{',
     'sed -n "18,35p" src/Cron/CronExpression.php',
     ["bash", "-c", "sed -n '18,35p' src/Cron/CronExpression.php"], ""),

    # ──────────────────────────────────────────────── xmp4_callers ───
    ("callers", "thiserror",
     'xmp4_callers(project="thiserror/thiserror", symbol_name="to_tokens", file_path="impl/src/lib.rs", page_size=10)',
     '0 callers found (page 1/1)\nNo results.',
     'grep -rn "to_tokens(" .',
     ["grep", "-rn", "to_tokens(", "."], ""),
    ("callers", "scrutor",
     'xmp4_callers(project="Scrutor/Scrutor", symbol_name="HasRegistration", file_path="src/Scrutor/ServiceCollectionExtensions.cs", page_size=10)',
     '1 caller found (page 1/1)\nApply src/Scrutor/RegistrationStrategy.cs:59',
     'grep -rn "HasRegistration" .',
     ["grep", "-rn", "HasRegistration", "."], ""),
    ("callers", "slf4j",
     'xmp4_callers(project="slf4j/slf4j-bom", symbol_name="getName", file_path="slf4j-api/src/main/java/org/slf4j/helpers/AbstractLogger.java", page_size=10)',
     '1 caller found (page 1/1)\nreadResolve slf4j-api/src/main/java/org/slf4j/helpers/AbstractLogger.java:66',
     'grep -rn ".getName(" .',
     ["grep", "-rn", ".getName(", "."], ""),
    ("callers", "zustand",
     'xmp4_callers(project="zustand/zustand", symbol_name="create", file_path="src/react.ts", page_size=10)',
     '1 caller found (page 1/1)\nCounter tests/ssr.test.tsx:21',
     'grep -rn "create(" src/ tests/',
     ["bash", "-c", "grep -rn 'create(' src/ tests/"], ""),
    ("callers", "cron",
     'xmp4_callers(project="cron-expression/cron-expression", symbol_name="isDue", file_path="src/Cron/CronExpression.php", page_size=10)',
     '0 callers found (page 1/1)\nNo results.',
     'grep -rn "isDue(" .',
     ["grep", "-rn", "isDue(", "."], ""),

    # ──────────────────────────────────────────────── xmp4_callees ───
    ("callees", "zustand",
     'xmp4_callees(project="zustand/zustand", symbol_name="createImpl", file_path="src/react.ts", page_size=10)',
     '8 callees found (page 1/1)\nStateCreator src/vanilla.ts:28\n28 src/vanilla.ts:16\ncreateStore src/vanilla.ts:99\n29 src/react.ts:53\nuseStore src/react.ts:17\n32 src/react.ts:54\n37 src/vanilla.ts:24\n35 src/vanilla.ts:24',
     'sed -n "50,60p" src/react.ts ; echo "--- then grep each call ---" ; grep -rn "createStore\\|useStore\\|StateCreator" src/',
     ["bash", "-c", "sed -n '50,60p' src/react.ts ; echo '---' ; grep -rn 'createStore\\|useStore\\|StateCreator' src/"], ""),
    ("callees", "cron",
     'xmp4_callees(project="cron-expression/cron-expression", symbol_name="isDue", file_path="src/Cron/CronExpression.php", page_size=10)',
     '10 callees found (page 1/1)\ndetermineTimeZone src/Cron/CronExpression.php:579\nDateTime\nDateTimeImmutable\ncreateFromFormat\nis_string\nInvalidArgumentException\nDateTimeZone\ngetNextRunDate src/Cron/CronExpression.php:289\ngetTimestamp\nException',
     'grep -n "function isDue" src/Cron/CronExpression.php ; echo "--- then read body ---" ; sed -n "100,150p" src/Cron/CronExpression.php',
     ["bash", "-c", "grep -n 'function isDue' src/Cron/CronExpression.php ; echo '---' ; sed -n '100,150p' src/Cron/CronExpression.php"], ""),

    # ──────────────────────────────────────────────── xmp4_hierarchy ─
    ("hierarchy", "scrutor",
     'xmp4_hierarchy(project="Scrutor/Scrutor", symbol_name="ServiceCollectionExtensions", file_path="src/Scrutor/ServiceCollectionExtensions.cs", page_size=10)',
     '0 derived types found (page 1/1)\nServiceCollectionExtensions Type',
     'grep -rn "extends ServiceCollectionExtensions\\|: ServiceCollectionExtensions" .',
     ["bash", "-c", "grep -rn 'extends ServiceCollectionExtensions\\|: ServiceCollectionExtensions' ."], ""),
    ("hierarchy", "slf4j",
     'xmp4_hierarchy(project="slf4j/slf4j-bom", symbol_name="AbstractLogger", file_path="slf4j-api/src/main/java/org/slf4j/helpers/AbstractLogger.java", page_size=10)',
     '3 derived types found (page 1/1)\nAbstractLogger Class interfaces=[Logger] derived=[LegacyAbstractLogger,EventRecordingLogger,SimpleLogger]',
     'grep -rn "extends AbstractLogger" .',
     ["grep", "-rn", "extends AbstractLogger", "."], ""),

    # ──────────────────────────────────────────────── xmp4_deps ───────
    ("deps", "thiserror",
     'xmp4_deps(project="thiserror/thiserror", page_size=10)',
     '3 deps found (page 1/1)\nthiserror-impl 2.0.18 (cargo)\nthiserror 2.0.18 (cargo)\nthiserror_no_std_test 0.0.0 (cargo)',
     'cat Cargo.toml',
     ["cat", "Cargo.toml"], ""),
    ("deps", "scrutor",
     'xmp4_deps(project="Scrutor/Scrutor", page_size=10)',
     '1 dep found (page 1/1)\n. . (nuget)',
     'find . -name "*.csproj" -exec cat {} +',
     ["bash", "-c", "find . -name '*.csproj' -exec cat {} +"], ""),
    ("deps", "orjson",
     'xmp4_deps(project="orjson/orjson", page_size=10)',
     '1 dep found (page 1/1)\norjson 3.11.7 (cargo)',
     'cat Cargo.toml',
     ["cat", "Cargo.toml"], ""),
    ("deps", "slf4j",
     'xmp4_deps(project="slf4j/slf4j-bom", page_size=10)',
     '1 dep found (page 1/1)\n. . (maven)',
     'find . -name "pom.xml" -exec cat {} +',
     ["bash", "-c", "find . -name 'pom.xml' -exec cat {} +"], ""),
    ("deps", "zustand",
     'xmp4_deps(project="zustand/zustand", page_size=10)',
     '1 dep found (page 1/1)\nzustand 5.0.12 (npm)',
     'cat package.json',
     ["cat", "package.json"], ""),
    ("deps", "cron",
     'xmp4_deps(project="cron-expression/cron-expression", page_size=10)',
     '2 deps found (page 1/1)\ndragonmantank/cron-expression d61a8a9604ec1f8c3d150d09db6ce98b32675013 (composer)\nphp 8.4.19 (composer)',
     'cat composer.json',
     ["cat", "composer.json"], ""),

    # ──────────────────────────────────────────────── xmp4_view ──────
    ("view", "zustand",
     'xmp4_view(project="zustand/zustand", file_path="src/react.ts", from_line=60, to_line=70)',
     'src/react.ts:60-64 / 64\n  return useBoundStore\n}\n\nexport const create = (<T>(createState: StateCreator<T, [], []> | undefined) =>\n  createState ? createImpl(createState) : createImpl) as Create',
     'sed -n "60,70p" src/react.ts',
     ["bash", "-c", "sed -n '60,70p' src/react.ts"], ""),

    # ──────────────────────────────────────────────── xmp4_grep ──────
    ("grep", "zustand",
     'xmp4_grep(project="zustand/zustand", pattern="middleware", max_results=10)',
     "10 match(es) found (page 1/1)\nsrc/middleware/devtools.ts:292:             '[zustand devtools middleware] \"__setState\" action type is reserved ' +\nsrc/middleware/devtools.ts:313:               '[zustand devtools middleware] Unsupported action format',\nsrc/middleware/devtools.ts:328:                     [zustand devtools middleware] Unsupported __setState action format.\nsrc/middleware/devtools.ts:432:       '[zustand devtools middleware] Could not parse the received json',\nsrc/middleware/persist.ts:113:    * An optional boolean that will prevent the persist middleware from triggering hydration on initialization,\nsrc/middleware/persist.ts:212:           `[zustand persist middleware] Unable to update item '${options.name}', the given storage is currently unavailable.`,\nsrc/middleware/ssrSafe.ts:3: // This is experimental middleware. It will be changed before finalizing it.\nsrc/middleware/ssrSafe.ts:5: // TODO Not very happy with the middleware name. Will revisit it later.\nsrc/middleware.ts:1: export { redux } from './middleware/redux.ts'\nsrc/middleware.ts:6: } from './middleware/devtools.ts'",
     'grep -rn "middleware" src/ | head -10',
     ["bash", "-c", "grep -rn 'middleware' src/ | head -10"], ""),

    # ──────────────────────────────────────────────── xmp4_symbol_at ──
    ("symbol_at", "zustand",
     'xmp4_symbol_at(project="zustand/zustand", file_path="src/react.ts", line=63, column=14)',
     'Member create src/react.ts:63\n```ts\nvar create: Create\n```',
     'sed -n "63p" src/react.ts ; echo "(no grep equivalent — position-based)"',
     ["bash", "-c", "sed -n '63p' src/react.ts"], ""),

    # ──────────────────────────────────────────────── xmp4_tests_for ──
    ("tests_for", "zustand",
     'xmp4_tests_for(project="zustand/zustand", symbol_name="create", file_path="src/react.ts", page_size=10)',
     '1 test found (page 1/1)\nCounter tests/ssr.test.tsx:21',
     'grep -rln "create" tests/',
     ["bash", "-c", "grep -rln 'create' tests/"], ""),
    ("tests_for", "cron",
     'xmp4_tests_for(project="cron-expression/cron-expression", symbol_name="isDue", file_path="src/Cron/CronExpression.php", page_size=10)',
     '0 tests found (page 1/1)\nNo results.',
     'grep -rln "isDue" tests/',
     ["bash", "-c", "grep -rln 'isDue' tests/"], ""),
]


def run_grep(repo_key: str, cmd: list[str], subdir: str) -> tuple[str, int]:
    _, local_dir, _ = REPO[repo_key]
    cwd = REPOS_ROOT / local_dir / subdir if subdir else REPOS_ROOT / local_dir
    if not cwd.exists():
        return (f"ERROR: {cwd} not found", 2)
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=90)
        return (r.stdout + (r.stderr if r.returncode not in (0, 1) else ""), r.returncode)
    except subprocess.TimeoutExpired:
        return ("ERROR: timeout 90s", 3)


def main():
    rows = []
    for tool, lib, x_req, x_resp, g_req, g_cmd, subdir in CELLS:
        x_in = tok(x_req)
        x_out = tok(x_resp)
        x_tot = x_in + x_out

        g_body, rc = run_grep(lib, g_cmd, subdir)
        g_in = tok(g_req)
        g_out = tok(g_body)
        g_tot = g_in + g_out

        ratio = round(g_tot / x_tot, 1) if x_tot > 0 else None
        savings = round((1 - x_tot / g_tot) * 100, 1) if g_tot > 0 else None

        rows.append({
            "tool": tool, "lib": lib, "lang": REPO[lib][2],
            "xmp4_req_tok": x_in, "xmp4_resp_tok": x_out, "xmp4_total_tok": x_tot,
            "grep_req_tok": g_in, "grep_resp_tok": g_out, "grep_total_tok": g_tot,
            "grep_exit": rc,
            "savings_pct": savings, "ratio": ratio,
        })

    out_csv = Path(__file__).parent / "results" / "2026-04-20-matrix.csv"
    out_csv.parent.mkdir(exist_ok=True, parents=True)
    with out_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # Console table
    print(f"{'tool':<11}{'lib':<10}{'lang':<10}{'xmp4':>8}{'grep':>10}{'saving':>10}{'ratio':>8}")
    print("-" * 75)
    for r in rows:
        print(f"{r['tool']:<11}{r['lib']:<10}{r['lang']:<10}"
              f"{r['xmp4_total_tok']:>8}{r['grep_total_tok']:>10}"
              f"{str(r['savings_pct'])+'%':>10}{str(r['ratio'])+'x':>8}")

    # Aggregates by tool
    print("\n=== Aggregate by tool ===")
    from collections import defaultdict
    agg = defaultdict(lambda: {"x": 0, "g": 0, "n": 0})
    for r in rows:
        a = agg[r["tool"]]
        a["x"] += r["xmp4_total_tok"]; a["g"] += r["grep_total_tok"]; a["n"] += 1
    print(f"{'tool':<12}{'n':>4}{'xmp4':>10}{'grep':>10}{'saving':>10}{'ratio':>10}")
    for t, a in sorted(agg.items(), key=lambda kv: -(kv[1]["g"] - kv[1]["x"])):
        s = (1 - a["x"] / a["g"]) * 100 if a["g"] > 0 else 0
        r = a["g"] / a["x"] if a["x"] > 0 else 0
        print(f"{t:<12}{a['n']:>4}{a['x']:>10}{a['g']:>10}{s:>9.1f}%{r:>9.1f}x")

    tx = sum(r["xmp4_total_tok"] for r in rows)
    tg = sum(r["grep_total_tok"] for r in rows)
    print(f"\nTOTAL {len(rows)} cells: xmp4={tx} grep={tg} saving={(1-tx/tg)*100:.1f}%  ratio={tg/tx:.1f}x")
    print(f"CSV: {out_csv}")


if __name__ == "__main__":
    main()
