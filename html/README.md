# html/ — example4.ai landing page

Static HTML served from the cluster as `https://example4.ai`.

## Files

| File | Purpose |
|---|---|
| `index.html` | Current landing — hero with animated particles, stat section consuming `/api/stats`, benchmark, CTA, footer disclaimer. |
| `v2.html` | Alternative redesign (short-form). Not served yet — for A/B evaluation. |
| `README.md` | This file. Rules for maintenance. |

## How it's served

- **Source of truth**: this directory (`lsai-xmp4.public/html/`).
- **Cluster resource**: ConfigMap `landing-page-html` in namespace `example4`.
- **Pod**: `landing-page` deployment (nginx) mounts the ConfigMap at `/usr/share/nginx/html/`.
- **Ingress**: Traefik serves `example4.ai` + `www.example4.ai` to the pod.
- **DNS**: `example4.ai` → `167.235.104.182` (Hetzner LB).

## Update procedure (for any assistant touching this)

**Always** follow these 3 steps in order. Never edit files directly in the cluster.

### 1. Edit `index.html` (or `v2.html`) here, commit, push

```bash
cd /home/laco/lsai-xmp4.dashboard/submodules/lsai-xmp4.public
# edit html/index.html
git add html/
git commit -m "chore(landing): <what changed>"
git push origin main
```

### 2. Redeploy ConfigMap + pod

```bash
export KUBECONFIG=/home/laco/lsai-xmp4.dashboard/kubeconfig.yaml
cd /home/laco/lsai-xmp4.dashboard/submodules/lsai-xmp4.public

kubectl -n example4 create configmap landing-page-html \
    --from-file=index.html=html/index.html \
    --dry-run=client -o yaml | kubectl apply -f -

kubectl -n example4 rollout restart deployment/landing-page
kubectl -n example4 rollout status deployment/landing-page --timeout=60s
```

### 3. Smoke test

```bash
# Fresh fetch (cache-bust)
curl -s "https://example4.ai/?v=$(date +%s)" -o /tmp/live.html
wc -c /tmp/live.html                                             # expect ≈ 58KB
grep -c 'Projects navigable' /tmp/live.html                      # expect 2
grep -c 'data-stat-key' /tmp/live.html                           # expect 6
grep -cE 'SCIP-indexed|SCIP projects|SCIP-resolved' /tmp/live.html   # expect 0
```

## Content rules (IMMUTABLE until user says otherwise)

These rules reflect explicit user directives. Violate → the user will be angry.

### 1. No "SCIP" or "Sourcegraph" in marketing copy

SCIP may appear **only** in the footer disclaimer with Apache 2.0 credit and the explicit "not affiliated with or endorsed by Sourcegraph" clause. Nowhere else.
If you find SCIP in any `hero-*`, `solution-*`, `powered-*`, `stat*`, `how-step*`, or `compare-*` block, remove it.

### 2. Stat numbers are live (via `/api/stats`)

Repo/project/language counters must come from `https://dashboard.example4.ai/api/stats`.
- HTML keeps static fallback values (`data-target="547"`, `"9145"`, `"10"`) for graceful degradation on fetch error.
- JS `fetch` updates `data-target` attributes with `data-stat-key="repos|projects|languages"` before the IntersectionObserver animates.
- Same JS rewrites `T.en` / `T.it` i18n tables replacing `547` → live repos, `10 languages` → live language count. Ensures hero-sub, hero-note, solution-desc show the same live numbers as the stat section (no contradictions).

### 3. Italian + English parity

Every string in `T.en` must have a matching key in `T.it`. `data-i18n="key"` lookup without match = visible untranslated key = bug.

### 4. CORS origin must match

The API CORS policy (`public-stats`) whitelists `https://example4.ai` and `https://www.example4.ai` only. If the landing moves to a different domain, update `AddCors` in `src/Zerox.Lsai.Server/Program.cs` first, then redeploy the server.

### 5. Disclaimer must stay in footer

Structure: "xmp4 builds on SCIP (Apache 2.0 link) / not affiliated with Sourcegraph / OSS libraries remain property of their authors / privacy link". Both EN + IT.

## Things to NOT touch without asking

- `particles` canvas + `ambient` orbs + `grid-bg` — user likes the current visual effect.
- Language switcher (EN/IT toggle) — must work, persisted in `localStorage`.
- Typing effect on `hero-headline` — cosmetic but user-requested.

## Things you MAY freely edit

- Copy in any section (with rules above respected).
- Order of sections (except hero which stays first).
- Add new sections or remove entire ones if user asks.
- CSS tweaks (colors in `:root` vars, spacing, animations).

## Do NOT

- Do NOT create a new `example4-ai` repo — that one is archived. Source lives here, in this directory.
- Do NOT edit the ConfigMap directly via `kubectl edit` — always regenerate from this directory (step 2 above) so git stays the source of truth.
- Do NOT put live credentials, API keys, secrets, bearer tokens in HTML.
- Do NOT add third-party trackers (Google Analytics, Facebook Pixel, ...) — user has not approved it.

## Related

- Server API: `/api/stats` implementation in `src/Zerox.Lsai.Server/Controllers/StatsController.cs` (task 36).
- Backend CORS: `src/Zerox.Lsai.Server/Program.cs`, policy `public-stats`.
- OPS.md §13 `Redeploy landing page (example4.ai)` — same steps in condensed form.
