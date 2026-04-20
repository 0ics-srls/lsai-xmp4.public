# Privacy — What xmp4 logs, what it doesn't

**Last reviewed**: 2026-04-20 · **Applies to**: the hosted endpoint at `https://mcp.example4.ai/mcp`

---

## In short

xmp4 is a **read-only semantic lookup** service over pre-indexed open-source libraries. It never receives your codebase, your files, or your identity. It logs the queries it serves so we can grow the library index by demand.

## What we log

Each tool call we serve records, in **aggregate rolling totals**, the following fields:

- **Tool name** (e.g. `xmp4_search`, `xmp4_callers`).
- **Project identifier** (e.g. `flask/Flask` — the OSS library being queried, not your code).
- **Symbol name** or search query string (e.g. `"Flask"`, `"JoinHandle"`).
- **Coarse timestamp** (bucketed by hour, for trend analysis).

These aggregate tallies are what drives *demand-driven coverage growth*: when many agents request a project we don't index, we see it and queue it.

## What we do not log

- **No content of your local codebase.** xmp4 only receives the name of an OSS symbol/project — never your files, paths from your machine, or any text you typed into your editor.
- **No user identity.** No account, no email, no IP address tied to a profile. The hosted endpoint is open-auth for the free tier.
- **No request bodies beyond the declared tool parameters.** The MCP protocol lets us inspect only the parameters you pass.
- **No response caching tied to an identifier.** The per-project SCIP index is cached in RAM globally, not per user.

## Network-level record retention

Our reverse proxy (nginx) writes ephemeral request logs containing source IP, User-Agent, request path, and response size — the standard of any HTTPS service. These logs are kept **7 days for operational debugging** and then purged. They are not joined against the aggregate tool-call tallies and are not used to build user profiles.

## Open-aggregate-stats endpoint (planned)

We plan to publish a `GET /stats/top-missing` endpoint that returns, in anonymized aggregate, the top project identifiers that were queried but not found in the index — the exact signal we use to prioritize which OSS repo to add next. Full transparency on what drives the growth loop.

Status: design stage, not yet live. Issue tracking the work: [#TBD once repo is public].

## What this means for an enterprise that wants to use xmp4

- The hosted endpoint is fine for any developer personally or for public OSS exploration.
- For teams with strict data-egress policies that forbid any external call from an AI tool: xmp4 receives only symbol/project names, but the decision is yours — consult your security review.
- A self-hosted deployment of xmp4 is not currently offered publicly. If this is a blocker for your team, open a feature request.

## Contact

Privacy concerns or data-subject inquiries (EU/UK residents exercising rights under GDPR/UK-GDPR): open an issue marked `privacy` on this repository. We will respond from the repository-owner contact listed on GitHub.

## Changes to this document

We version this file in git. Material changes will be announced in the repository README under *Status* for 30 days before the new version takes effect.
