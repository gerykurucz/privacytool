# Architecture — how SnappyAI entitlements work (v14)

## The whole system in one picture

```
        customer pays / cancels / renews
                     │
                     ▼
        ┌─────────────────────────┐
        │  Stripe                 │  (test mode today; live later)
        └───────────┬─────────────┘
                    │ webhook, signed with whsec_…
                    ▼
        ┌─────────────────────────────────────────────┐
        │  Cloudflare Worker "publisher-simple"       │
        │  POST /webhooks/stripe   (~400 ms)          │
        │  GET  /healthz  /entitlements.json          │
        │  POST /admin/{lookup,grant,publish}         │
        │  cron 0 * * * * (keepalive republish)       │
        │                                             │
        │  secrets: ED25519_SECRET, GITHUB_PAT,       │
        │           STRIPE_WEBHOOK_SIGNING_SECRET,    │
        │           ADMIN_TOKEN                       │
        └───────────┬─────────────────────────────────┘
                    │ read-modify-write (compare-and-swap via blob SHA)
                    ▼
        ┌─────────────────────────────────────────────┐
        │  PUBLIC repo gerykurucz/snappyai-entitlements│
        │  branch live → entitlements.json (signed)   │
        │  = the ONLY storage. No DB, no KV, no D1.   │
        └───────────┬─────────────────────────────────┘
                    │ anonymous HTTPS fetch (raw.githubusercontent.com)
                    ▼
        ┌─────────────────────────────────────────────┐
        │  Desktop client (src/app)                   │
        │  online.py  – fetch, verify, gate           │
        │  edsig.py   – Ed25519 verify, pinned pubkey │
        │  Discord OAuth token exchange (client-side, │
        │  uses DISCORD_CLIENT_SEC from build_secrets)│
        └─────────────────────────────────────────────┘
```

## The state file — storage AND publication in one document

`entitlements.json` on branch `live`:

```json
{
  "v": 1,
  "generated_at": 1790980695,     // freshness clock; clients fail closed at 6 h
  "cursor":       1790980695,     // Stripe event cursor (created-timestamp)
  "rows":  { "<sha256('email:'+addr)>": {"until":…, "status":…, "plan":…} },
  "seen":  [ "evt_…", … ],        // idempotency list, capped at 500
  "subs":  { "sub_…": "<row hash>" },   // cancellation → row lookup
  "pis":   { "pi_…":  "<row hash>" },   // payment-intent → row lookup
  "sig":   "base64 Ed25519 over everything above"
}
```

Why the extra keys (`seen`, `subs`, `pis`) don't break shipped clients:
`online._canonical_bytes()` canonicalises over **every** key except `sig`
(sorted keys, compact separators), so old clients happily verify the richer
document while reading only `rows` and `generated_at`.

Why one file and not two (private state + public document, as the old design
had): one file is atomically consistent by construction — the write either
happens or it doesn't, and there is nowhere else to keep in step.

Honest cost: the repo is public, so Stripe subscription ids (`subs`) and
event ids (`seen`) are public too. Neither is a credential, but they are
metadata. Row keys remain `sha256("email:"+addr)` — crackable against an
email wordlist, so the subscriber count is effectively public. See
`SECURITY-INCIDENT.md` item 4.

## Write path — webhook to commit

1. **Authenticate**: recompute the Stripe signature header (t, v1 HMAC with
   `STRIPE_WEBHOOK_SIGNING_SECRET`) and compare; reject on mismatch or if the
   timestamp is stale. Replay of an old *valid* event is handled by `seen`.
2. **Read** the current file via GitHub Contents API (also yields the blob SHA).
   - 404 → fresh empty state, first write CREATEs the file.
   - Placeholder (`generated_at == 0`) → replaced in memory with empty state.
3. **Apply** the event (idempotent — events in `seen` are skipped):
   - `checkout.session.completed` → create/extend the row from the session
     (email or customer id; three id shapes handled), record `subs`/`pis`.
   - `invoice.paid` → extend `until` to the new period end. **Stripe "Basil"**
     moved `current_period_end` off the Subscription object onto
     `items.data[n]`; the Worker reads it from the item first.
   - `invoice.payment_failed` → mark the row `past_due` (grace, not instant revoke).
   - `customer.subscription.updated` / `.deleted` → adjust or end the row.
     These events carry **no email** — the row is found via `subs[sub_id]`.
   - `charge.refunded` → revoke.
4. **Sign** with `ED25519_SECRET` (tweetnacl, vendored). The Worker first
   checks the derived public key equals the baked-in pin
   `J3Ulxeu/JPzIlGypJ28+h45rlw3aW6bJFfDu3luRGOE=` and **refuses to sign**
   otherwise — a wrong seed is a loud error, never a silent lockout.
5. **Write** via Contents API **with the blob SHA** → compare-and-swap.
   Concurrent webhooks can't clobber each other: the loser gets 409,
   re-reads, re-applies, retries. (The old pipeline needed a
   `git push --force` + concurrency group + row-floor guard for this; the
   row-floor sanity check — refuse to publish if rows drop below 40% of the
   previous count — is kept as a belt-and-braces guard anyway.)

## Freshness

Clients fail closed when `generated_at` is older than `FRESHNESS_SECONDS = 6 h`
(`online.py`). The Worker's hourly cron (`0 * * * *`) republishes with a fresh
timestamp even when nothing happened, so silence from Stripe never locks
customers out. `raw.githubusercontent.com` CDN caching is handled by the
client's cache-busting/freshness logic.

## Client verification path (`online.py` + `edsig.py`)

1. Fetch the file (repo/branch from `build_secrets.entitlement_repo()`).
2. Check `generated_at` freshness (fail closed).
3. Rebuild the canonical bytes (sorted keys, compact separators, minus `sig`)
   and verify the Ed25519 signature against the **pinned** public key from
   `build_secrets.entitlement_pubkey()`. `edsig.py` is a dependency-free
   RFC 8032 implementation; Ed25519 is deterministic, so its verification is
   byte-compatible with the Worker's tweetnacl signatures — proven by
   `tests/prove-edsig-interop.mjs` + `tests/verify-with-edsig.py`, which run
   the client's own unmodified module against Worker output.
4. Look up the signed-in user's row: `sha256("email:" + address)` (with a
   legacy unpeppered fallback), compare `until` against now, honour `status`.
5. Discord sign-in: OAuth PKCE-less code flow with `DISCORD_CLIENT_ID` /
   `DISCORD_CLIENT_SEC` — **client-side by design in this edition**; the
   secret is obfuscated in `_BLOB`, not encrypted (threat model in
   `build_secrets.py`'s docstring and `SECURITY-INCIDENT.md` item 2).

## Admin surface

All under `x-admin-token`:

- `GET /admin/lookup?email=…` — the row + sub/pi mappings for one customer
  (support: "why am I locked out?").
- `POST /admin/grant {email, days, reason}` — manual time (replaces
  `builder.py --grant`).
- `POST /admin/publish` — force an immediate re-sign + commit.
- `GET /healthz` — configuration + freshness report (public; no secrets in it).
- `GET /entitlements.json` — debug mirror served by the Worker itself.

## What this architecture deliberately does NOT do

- **No prevention of account sharing.** The `shared` flag is detection-only
  (presence ping webhook), and the Worker does not scan the presence channel,
  so detection is currently dormant. Real prevention needs real-time state —
  a Cloudflare Durable Object holding a per-row session counter, same free
  plan. Proposed, not built.
- **No private per-client grants.** Everyone fetches the same public file;
  privacy rests on the email hash. Removing that exposure means either a
  pepper (coordinated Worker+client change: the Worker would write BOTH
  peppered and unpeppered rows during a transition, clients switch, then
  unpeppered rows are dropped) or per-client signed grants from an
  authenticated endpoint — a bigger redesign.
- **No live billing yet.** Stripe links in the client are test-mode; the
  webhook endpoint must be re-pointed/re-secreted when you flip to live
  (`WORKER-SETUP.md` Step 6.5).

## Failure modes, ranked

| Failure | Effect | Guard |
|---|---|---|
| Wrong/missing seed | Worker refuses to sign | pin check before every signature |
| PAT revoked/expired | publishes stop; file goes stale after 6 h | `/healthz` `read_error`; cron logs |
| Stripe secret wrong | all webhooks 400 | `/healthz` `webhook_secret_configured` |
| Concurrent webhooks | none — CAS retry | blob-SHA compare-and-swap |
| Bug deletes rows | refuse to publish | 40% row-floor guard |
| File 404 | clients fail closed | placeholder committed before Worker goes live |
| Worker totally down | clients keep working off the last fresh file (≤6 h) | freshness window |
