# Request a library

xmp4 currently indexes 547 repositories (9 145 SCIP-indexed projects). If the library you need isn't in the index, tell us — the request queue is a real signal in our prioritization.

## How the priority queue works

We rank requests by a **combined score**:

1. **Explicit requests** filed as issues on this repo (this template).
2. **Aggregate query demand** — if many AI agents blind-query a project we don't have, we see the miss in our aggregate logs and it contributes to the score.

One user request with real downstream query traffic almost always gets indexed within days. A request with zero downstream traffic may wait, but we see it and will revisit when we broaden a batch in that language.

## Before you file

- Check if your library is already indexed: search `xmp4_projects(language=…, query=…)` in your client. Many libraries are indexed under slightly different names (`flask/Flask`, not `pallets/flask`; `angular/ng-template`, not `angular/angular`).
- If it is a **monorepo** with dozens of sub-packages, one request covers the whole repo — we use the appropriate indexing strategy per language (1 SCIP + N sub-project views, or N SCIPs per sub-package, depending on the build system). You do not need to file 30 separate issues.
- If the repo is **private**, we cannot index it on the public endpoint. Self-hosted xmp4 deployment isn't offered publicly yet; file a feature request if you'd like that option.

## File the request

Open the **Repo request** issue template:

[→ New repo request](../../issues/new?template=request-repo.yml)

You'll be asked for:

- GitHub URL.
- Primary language.
- Preferred version / tag (or blank for latest stable).
- One real query you'd want to run — a concrete AI-agent task this unblocks (this helps us verify the repo is useful, not just popular).
- Whether it's a monorepo.

## What happens next

1. The issue lands in the `repo-request` queue with `triage` label.
2. We check the aggregate query logs for the same project identifier.
3. If demand is clear or the repo is a top-500 OSS library, we schedule indexing in the next batch (usually within a week).
4. When indexing completes and the project is live, we close the issue with a link to `xmp4_projects(query=<your-repo>)` showing it indexed.

## Supported languages (today)

**Tier 1** (full coverage): C#, TypeScript, Python, Java, Rust, PHP.
**Tier 2** (best-effort, indexer quirks possible): Go, JavaScript, Dart, Ruby, C++.

A request on a tier-2 language is still welcome. We may flag known upstream SCIP-tool limitations (for example, `xmp4_hierarchy.base` being empty for TypeScript due to scip-typescript's current behavior) in our reply so you know what to expect.

## Not sure if it's indexable?

Some upstream SCIP tools have known gaps (scip-clang on very large C++ projects, scip-ruby on certain gem layouts, scip-go when the repo uses non-standard GOPATH conventions). In those cases we'll still investigate and tell you what works vs. what doesn't — preferred over silently dropping the request.

Put anything you know up front (custom build, unusual layout, indexer you've tried before) in the *Anything else* field of the template.
