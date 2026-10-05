# Secret map — every credential, exactly one home

Rule of thumb: **the Worker holds publishing power, the client holds sign-in
power, and they never share a credential.** If a value appears in both
columns below, something is wrong.

```
                    ┌──────────────────────────────┐
   Stripe ─webhook─▶│  Cloudflare Worker           │
                    │  publisher-simple            │──▶ GitHub public repo
                    │  4 secrets (below)           │    (signed entitlements.json)
                    └──────────────────────────────┘              │
                    ┌──────────────────────────────┐              │ fetch
   Discord ◀─OAuth─▶│  Desktop client (exe)        │◀─────────────┘
                    │  src/app/build_secrets.py    │
                    │  _BLOB constants (below)     │
                    └──────────────────────────────┘
```

---

## A. Worker secrets — Cloudflare dashboard ONLY

dash.cloudflare.com → **Workers & Pages** → `publisher-simple` →
**Settings → Variables and Secrets**. Type = **Secret** for all four.

| Secret | What it is | Status (2026-10-03) | Where the value comes from |
|---|---|---|---|
| `ED25519_SECRET` | the signing seed — signs `entitlements.json` | ✅ **already saved & correct** (healthz shows the new pubkey) | `docs/NEW-SIGNING-KEY.txt` |
| `GITHUB_PAT` | fine-grained PAT, Contents R/W on `snappyai-entitlements` ONLY | ❌ missing → `docs/WORKER-SETUP.md` Step 2+4 | github.com → Settings → Developer settings → Fine-grained tokens |
| `STRIPE_WEBHOOK_SIGNING_SECRET` | the `whsec_...` that proves a webhook really came from Stripe | ❌ missing → Step 6+4 | Stripe → Developers → Webhooks → your endpoint → Reveal |
| `ADMIN_TOKEN` | guards `/admin/lookup`, `/admin/grant`, `/admin/publish` | ❌ missing → Step 4 | you make it up (40+ random chars) |

**Never in the Worker:** the Discord client secret (there is no variable for
it, by design), the Discord client id, any Stripe *secret key*, payment
links, the presence webhook.

---

## B. Client constants — `src/app/build_secrets.py` → `_BLOB` ONLY

These are XOR-obfuscated in the source (recoverable by a determined attacker
with the exe — unavoidable for any installed app; see `docs/SECURITY-INCIDENT.md`).

| `_BLOB` key | What it is | Status | Notes |
|---|---|---|---|
| `DISCORD_CLIENT_SEC` | **← THE Discord secret goes HERE.** OAuth token exchange, client-side | set — **rotate it** (it was recoverable from the old source), then re-encode | discord.com/developers → your app → OAuth2 → Reset Secret → `python encode_secret.py DISCORD_CLIENT_SEC "<new>"` → paste the printed line into `_BLOB` |
| `DISCORD_CLIENT_ID` | public OAuth client id (`1553859545674154014`) | set | not secret; only changes with a new Discord app |
| `ENTITLEMENT_PUBKEY` | pinned NEW Ed25519 public key | ✅ set to the new key in this archive | decodes to `J3Ulxeu/JPzIlGypJ28+h45rlw3aW6bJFfDu3luRGOE=`; check with `python encode_secret.py --dump` |
| `ENTITLEMENT_REPO` | `gerykurucz/snappyai-entitlements` | ✅ set | |
| `ENTITLEMENT_BRANCH` | `live` | ✅ set | |
| `PRESENCE_WEBHOOK` | Discord webhook for presence pings | set — **delete & recreate the webhook** (URL is a bearer credential inside every exe) | `docs/SECURITY-INCIDENT.md` item 3 |
| `STRIPE_MONTHLY`, `STRIPE_TRIAL` | payment links shown in the paywall | ⚠️ still **test mode** — replace before taking real money | Stripe → Payment links |
| `ROW_PEPPER` | row-hash pepper | **MUST STAY EMPTY (`""`)** | The Worker keys rows by *unpeppered* `sha256("email:"+addr)`. Setting a pepper here orphans every customer — the client would look up rows that don't exist. A pepper rollout requires a coordinated Worker change first (`docs/ARCHITECTURE.md`). |

**Never in the client:** `ED25519_SECRET` (the seed), `GITHUB_PAT`,
`ADMIN_TOKEN`, `whsec_...`. If any of those ever ends up in an exe, anyone can
forge entitlements or edit the repo.

---

## C. Everywhere else

| Credential | Home | Never anywhere else |
|---|---|---|
| Stripe secret key (`sk_...`) | Stripe dashboard / old Actions only — **the Worker does not need it** (webhooks are verified with the `whsec_` alone) | not in the repo, not in the Worker, not in chat |
| Old GitHub Actions secrets (`snappyai-backend`) | delete with the workflow — the old builder is retired | — |
| The leaked fine-grained PAT (pasted into chat) | **revoked / to be revoked**; treat as public forever; never reissue it | it appears in NO file of this archive |

---

## D. Quick self-checks

```bash
# Worker: all four configured, new key pinned?
open https://publisher-simple.snappyai.workers.dev/healthz
#   → github_pat_configured / webhook_secret_configured /
#     signing_key_configured / pubkey_matches_expected  ALL true

# Client: constants decode to the right values? (masks credentials)
cd src/app && python encode_secret.py --dump
#   → ENTITLEMENT_PUBKEY = J3Ul...GOE=   ENTITLEMENT_REPO = gerykurucz/snappyai-entitlements
```

## E. Rotation cheat-sheet

| If this leaks… | …do this | Ripple |
|---|---|---|
| `GITHUB_PAT` | delete it on GitHub, make a new one, update the Worker secret | none — clients unaffected |
| `ADMIN_TOKEN` | invent a new one, update the Worker secret | none |
| `whsec_...` | rotate the endpoint secret in Stripe, update the Worker secret | none |
| Discord client secret | Reset Secret in Discord dev portal → encode into `_BLOB` → **rebuild + redistribute the exe** | every installed exe must be updated |
| `ED25519_SECRET` (the seed) | worst case: generate a new keypair, update the Worker secret, rebuild the bundle with the new pin, rebuild every client | total — see `docs/NEW-SIGNING-KEY.txt` §5 |
