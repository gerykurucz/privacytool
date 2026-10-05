# START HERE — SnappyAI v14

This archive is the **complete replacement** for your old "GitHub Actions
rebuilds entitlements.json every 10 minutes" pipeline. Subscriptions now
activate in **under a second** (Stripe webhook → Cloudflare Worker → signed
file in your public repo), and clients keep fetching the exact same URL they
always did.

Everything is browser-based. No terminal needed for setup (a terminal is only
ever needed if you rebuild the exe or edit Worker code).

---

## What is in this archive

```
snappyai-v14/
├── START-HERE.md  (in docs/)      ← you are here
├── README.md                      one-page overview of the layout
│
├── github/
│   ├── HOW-TO-CREATE-THE-REPO.md  click-by-click repo creation
│   └── snappyai-entitlements/     ← EXACTLY the 2 files to upload to the
│       ├── entitlements.json        public repo (placeholder + README)
│       └── README.md
│
├── worker/publisher-simple/
│   ├── worker.js                  ← THE file you upload to Cloudflare
│   └── source/                    dev project (only if you ever edit code)
│
├── src/app/                       client files — copy over the same-named
│   ├── build_secrets.py           files in your client source tree and
│   │                                rebuild the exe (NEW pubkey inside;
│   │                                Discord secret lives HERE)
│   ├── online.py  edsig.py  gui.py
│   ├── encode_secret.py           helper for rotating _BLOB values
│   └── README.md
│
├── docs/                          all documentation (see below)
└── tests/                         automated checks (optional, needs Node)
```

## The new public key

The signing key was rotated on 2026-10-03 (the old one is dead). The NEW
public key — already hardcoded everywhere in this archive — is:

```
J3Ulxeu/JPzIlGypJ28+h45rlw3aW6bJFfDu3luRGOE=
```

and the repo is hardcoded as `gerykurucz/snappyai-entitlements`. You never
need to type either one anywhere; they are baked into `worker.js` and into
`src/app/build_secrets.py`.

---

## Do these, in this order

| # | Task | Document | Time |
|---|---|---|---|
| 1 | Create the public repo + upload the 2 files | `github/HOW-TO-CREATE-THE-REPO.md` | 5 min |
| 2 | Finish the Worker: new GitHub token, re-upload `worker.js`, add 3 secrets, cron, Stripe webhook, prove it | `docs/WORKER-SETUP.md` | 15 min |
| 3 | **Disable the old GitHub Actions builder** (private repo `snappyai-backend`) — it holds the OLD key and would overwrite the file with signatures every new client rejects | `docs/NEW-SIGNING-KEY.txt` §4 | 2 min |
| 4 | Rotate the Discord client secret, put it in `src/app/build_secrets.py` (`_BLOB["DISCORD_CLIENT_SEC"]` — client only, NEVER the Worker), rebuild + distribute the exe | `docs/CLIENT-BUILD.md` + `docs/SECRET-MAP.md` | 30 min |
| 5 | Read the security list and tick off what you accept for now | `docs/SECURITY-INCIDENT.md` | 10 min |

**Current status of your live Worker**
(`https://publisher-simple.snappyai.workers.dev/healthz`, checked 2026-10-03):
signing secret ✅ saved and correct; deployed code ⚠️ stale (Step 2 fixes);
GitHub PAT ❌, Stripe webhook secret ❌, admin token ❌ (Step 2 adds them).

---

## The docs, one line each

| File | Read it when… |
|---|---|
| `docs/WORKER-SETUP.md` | setting up / finishing the Cloudflare Worker (**the main to-do list**) |
| `docs/SECRET-MAP.md` | you wonder "where does X go?" — every credential's one home |
| `docs/NEW-SIGNING-KEY.txt` | you need the signing seed again, or ever rotate keys |
| `docs/ARCHITECTURE.md` | you want to understand how the whole thing works |
| `docs/CLIENT-BUILD.md` | rebuilding/shipping the desktop exe |
| `docs/SECURITY-INCIDENT.md` | what was exposed, what's fixed, what's accepted risk |

## Optional: run the tests

If you have Node.js 18+ on any machine:

```bash
node --test tests/          # 133 tests: worker logic + the uploaded bundle
bash tests/check-deploy.sh  # full pre-flight: layout, pins, freshness, interop
```

`check-deploy.sh` also proves the Worker's signature verifies under your
client's own `src/app/edsig.py` — the exact code path a customer's exe runs.

---

## One-paragraph summary of the system

Stripe sends a webhook to the Worker the moment a payment lands. The Worker
verifies it with the `whsec_` signing secret, updates a row keyed by
`sha256("email:" + address)` in a single JSON state file, signs the whole
document with the Ed25519 seed (Cloudflare holds the only copy), and commits
it to the `live` branch of the public repo via a narrowly-scoped PAT. An
hourly cron keeps the timestamp fresh; clients fail closed if the file is
older than 6 hours or the signature doesn't match the pinned public key.
Support tools (`/admin/lookup`, `/admin/grant`, `/admin/publish`) are guarded
by the admin token. No database, no server, no 10-minute waits.
