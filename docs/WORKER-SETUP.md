# Worker setup — publisher-simple (browser only, no terminal)

Your Worker **already exists** at:

```
https://publisher-simple.snappyai.workers.dev
```

and one of the four secrets (`ED25519_SECRET`) is already saved correctly.
What remains, in order:

| # | Step | Where | Status right now |
|---|---|---|---|
| 1 | Create the public repo + placeholder file | github.com | to do (5 min) — see `github/HOW-TO-CREATE-THE-REPO.md` |
| 2 | Make a NEW GitHub token | github.com | to do (3 min) |
| 3 | Re-upload the Worker code (fixes the stale bundle) | dash.cloudflare.com | to do (3 min) |
| 4 | Add the three missing secrets | dash.cloudflare.com | to do (5 min) |
| 5 | Check the hourly cron trigger | dash.cloudflare.com | verify (1 min) |
| 6 | Point Stripe at the Worker | dashboard.stripe.com | to do (5 min) |
| 7 | Prove it works end to end | browser | to do (2 min) |

**No database, no wrangler, no npm, no terminal.** Storage is one JSON file
in your public repo; the Worker maintains it.

```
Stripe  ──webhook──▶  Cloudflare Worker  ──▶  ONE json file in your public repo
                       (~400 ms)                    (signed, Ed25519)
                                                          │
                            your shipped clients fetch it anonymously ◀┘
```

---

## Where you stand (checked 2026-10-03)

`https://publisher-simple.snappyai.workers.dev/healthz` currently reports:

```json
"signing_key_configured": true,          ✅ ED25519_SECRET is saved and correct
"ed25519_pubkey": "J3Ulxeu/JPzIlGypJ28+h45rlw3aW6bJFfDu3luRGOE=",   ✅ the NEW key
"pubkey_matches_expected": false,        ⚠️ the deployed CODE is a stale bundle
                                            that still pins the OLD key
                                            → fixed by Step 3 (re-upload)
"github_pat_configured": false,          ⚠️ Step 2 + Step 4
"webhook_secret_configured": false,      ⚠️ Step 6 + Step 4
"read_error": "GITHUB_PAT is not configured"
```

So: the signing key is done, everything else is below.

---

## Step 1 — the public repo

Full click-by-click instructions live next to the files themselves:
**`github/HOW-TO-CREATE-THE-REPO.md`**. Short version: create public repo
`gerykurucz/snappyai-entitlements`, create branch `live`, upload the two
files from `github/snappyai-entitlements/`, then confirm this URL shows the
placeholder JSON:

```
https://raw.githubusercontent.com/gerykurucz/snappyai-entitlements/live/entitlements.json
```

---

## Step 2 — make a GitHub token (a NEW one)

> ⚠️ The token you pasted into chat earlier is **compromised forever** — if
> you haven't already, delete it at
> https://github.com/settings/personal-access-tokens first. Make a fresh one
> here, and **do not paste it into any chat, including this one.** It goes
> straight from GitHub's page into Cloudflare (Step 4).

1. github.com → **Settings** (your avatar, top right) → **Developer settings**
   (very bottom of the left menu) → **Personal access tokens** → **Fine-grained tokens**
2. **Generate new token**
3. Name: `snappyai-publisher`
4. Repository access: **Only select repositories** → `snappyai-entitlements`
5. Permissions → **Repository permissions** → **Contents** → **Read and write**
6. Generate, and **copy the token now** — GitHub shows it once

This token can only write that one public repo. That's the whole blast radius.

---

## Step 3 — re-upload the Worker code

The bundle you deployed earlier pins the OLD public key (that's why
`pubkey_matches_expected` is `false`). The file in this archive is the
correct, current one:

```
worker/publisher-simple/worker.js
```

1. dash.cloudflare.com → **Workers & Pages** → **publisher-simple** → **Edit code**
2. In the file tree on the left, delete everything **except** `worker.js`
   (any `src/` folder, `wrangler.toml`, `package.json`, zips — all of it).
   The tree must contain exactly one file: `worker.js`.
   > The dashboard's editor ignores `wrangler.toml` and cannot follow
   > `import ... from "./src/..."` — that is why the single-file bundle
   > exists. Upload ONLY this file, never the project folder.
3. Drag **`worker/publisher-simple/worker.js`** onto the editor and
   **overwrite** the existing `worker.js`.
   (Or: open it in a text editor, copy everything, select-all in the
   dashboard editor, paste.)
4. Click **Deploy** (top right).

Nothing to configure in the code: repo (`gerykurucz/snappyai-entitlements`),
branch (`live`), file (`entitlements.json`) and the pinned NEW public key
(`J3Ulxeu/JPzIlGypJ28+h45rlw3aW6bJFfDu3luRGOE=`) are **baked into the file**.

Your secrets survive a code deploy — the dashboard never deletes
Variables/Secrets when you re-upload code.

**The Problems panel must be empty** after upload. (Old builds showed red
squiggles like *"Cannot find name 'require'"* — false alarms from the vendored
crypto library's dead ES5 code paths. The current bundle is patched and
carries a `@ts-nocheck` banner. If you ever see them again, you uploaded a
stale file; `bash tests/check-deploy.sh` catches that before you do.)

After deploying, open
`https://publisher-simple.snappyai.workers.dev/healthz` —
`"pubkey_matches_expected"` must now be **true**. If it is still false, the
upload didn't take; redo this step.

---

## Step 4 — add the three missing secrets

Worker page → **Settings → Variables and Secrets → Add**, each with
Type = **Secret** (not Text):

| Name | Value | From |
|---|---|---|
| `GITHUB_PAT` | the token from Step 2 | github.com |
| `STRIPE_WEBHOOK_SIGNING_SECRET` | the `whsec_...` from Step 6 | do Step 6 first, then come back |
| `ADMIN_TOKEN` | a long random string you make up (40+ characters) | see tip below |

Click **Deploy** after saving so they take effect.

`ED25519_SECRET` is already saved — **do not touch it**. (If you ever need
it again: `docs/NEW-SIGNING-KEY.txt`.)

> Tip for `ADMIN_TOKEN`: open
> `https://www.random.org/cgi-bin/randbyte?nbytes=32&format=h`
> in a browser and use the 64 hex characters it shows. It guards the
> `/admin/...` support endpoints (lookup, grant, force-publish).

**No Text variables are needed.** (`PUBLIC_REPO`, `BRANCH`, `FILE_PATH`,
`ED25519_EXPECTED_PUBKEY` exist as optional overrides of the baked-in
defaults — today, don't add them.)

---

## Step 5 — check the hourly keepalive cron

Your client fails closed if the signed file is older than 6 hours
(`FRESHNESS_SECONDS` in `online.py`), so the Worker republishes hourly even
when nobody buys anything:

1. Worker page → **Settings → Triggers**
2. Under **Cron Triggers** there must be: `0 * * * *`
3. If not: **Add Trigger** → enter `0 * * * *` → Save.

---

## Step 6 — point Stripe at the Worker

1. dashboard.stripe.com → **Developers** → **Webhooks** → **Add endpoint**
2. Endpoint URL:
   ```
   https://publisher-simple.snappyai.workers.dev/webhooks/stripe
   ```
3. Events to send: **Select events** → search and tick these six:
   - `checkout.session.completed`
   - `invoice.paid`
   - `invoice.payment_failed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `charge.refunded`
4. Create, then open the endpoint → **Reveal** the **Signing secret**
   (`whsec_...`) → copy it → save it as `STRIPE_WEBHOOK_SIGNING_SECRET`
   (Step 4)
5. Your payment links are still **test mode** — create the endpoint in test
   mode for now, and remember that going live means a NEW endpoint (or the
   same URL added in live mode) whose `whsec_...` **replaces** the secret in
   Step 4.

> If any older webhook endpoint exists (e.g. the `stripe-relay` experiment or
> the old GitHub Actions dispatch), **delete it or remove these events** —
> two publishers fight over the file. One endpoint only.

---

## Step 7 — prove it works

1. Open in your browser:
   ```
   https://publisher-simple.snappyai.workers.dev/healthz
   ```
   You want **all** of:
   ```json
   { "ok": true,
     "state_file": "gerykurucz/snappyai-entitlements/entitlements.json@live",
     "github_pat_configured": true,
     "webhook_secret_configured": true,
     "signing_key_configured": true,
     "pubkey_matches_expected": true }
   ```
2. Stripe → Developers → Webhooks → your endpoint → **Send test webhook
   event** → `checkout.session.completed`.
3. Watch live, no terminal: Cloudflare → your Worker → **Logs** → **Begin log
   stream**. Within a second: the event is handled, and a commit lands on the
   `live` branch of the public repo containing a real signed document
   (`sig` + the test customer's row).
4. Paste the raw URL from Step 1 into https://edsig.dev-style check — or
   simpler, run the client: it must accept the file (signature verifies under
   the NEW pinned key) and show the test row as active.

---

## Support endpoints (after Step 4)

Plain HTTP — works from any browser REST client or Postman, header
`x-admin-token: <your ADMIN_TOKEN>`:

```bash
# Why is this customer locked out?
GET  https://publisher-simple.snappyai.workers.dev/admin/lookup?email=customer@example.com

# Give someone free time (replaces `builder.py --grant`)
POST https://publisher-simple.snappyai.workers.dev/admin/grant
     body: {"email":"customer@example.com","days":30,"reason":"chargeback grace"}

# Force a republish now (instead of waiting for the cron)
POST https://publisher-simple.snappyai.workers.dev/admin/publish

# Serve the signed document from the Worker itself (debug mirror of the repo file)
GET  https://publisher-simple.snappyai.workers.dev/entitlements.json
```

---

## Alternative: deploy with wrangler (CLI), if you ever want to

The dashboard route above is the recommended one. If you later prefer the
terminal, everything for it is in `worker/publisher-simple/source/`:

```bash
npm install -g wrangler
wrangler login
cd worker/publisher-simple/source
wrangler deploy                       # uses wrangler.toml + src/ directly
wrangler secret put ED25519_SECRET    # ...and the other three secrets
```

`wrangler.toml` needs **no edits** — worker name is `publisher-simple` (so it
updates the LIVE worker instead of creating a second one) and the real pinned
key is in it. The cron trigger comes from the toml automatically.

**Keep the two routes separate:** whichever deploys last wins. Don't switch
back and forth mid-day.

### If you edit the code later

`worker/publisher-simple/worker.js` is **generated** from `source/src/`.
Edit `src/`, then rebuild from `source/`:

```bash
npm install          # once — installs esbuild (dev tool only)
npm run bundle       # regenerates ../worker.js
cd ../../.. && node --test tests/    # 133 tests, includes the bundle itself
```

…then re-upload the new `worker/publisher-simple/worker.js` (Step 3).
Never hand-edit the bundle.

---

## What this gives you — and what it doesn't

**Gives you:** instant activation (~400 ms instead of 10–20 minutes),
automatic renewals, automatic revocation on cancellation/refund, idempotent
replays, no database, no server to run, no terminal needed.

**Does not give you:** the one-machine-at-a-time rule. That's still
*detection* (the client's presence ping), not *prevention* — and detection is
currently dormant because the Worker does not scan the presence channel.
Prevention needs a counter with real-time state (a Cloudflare Durable Object
on the same free account). Say the word and it gets built; get this running
first.

**Still exposes:** row keys are `sha256("email:"+address)` in a public file —
your subscriber list is crackable exactly as before. See
`docs/SECURITY-INCIDENT.md` item 4 for the two ways out.
