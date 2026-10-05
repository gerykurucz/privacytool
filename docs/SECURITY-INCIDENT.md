# SECURITY INCIDENT — credentials exposed, rotate in this order

Found while reviewing your attached files on 2026-10-03. **None of the secret
values are reproduced in this document** — you don't need them to rotate, and
writing them down again is how leaks spread.

> Paths below refer to the **v14 archive layout**: client files are
> `src/app/…`, the Worker bundle is `worker/publisher-simple/worker.js`, and
> the key handoff is `docs/NEW-SIGNING-KEY.txt`. Where each credential lives
> now: `docs/SECRET-MAP.md`.

Severity is ordered by what an attacker can actually do right now.

---

## 1. GitHub fine-grained PAT — pasted into chat — **CRITICAL, do this first**

You pasted a fine-grained PAT (the `github_pat_` prefixed one) into this conversation. Assume it is public.

**Revoke:** https://github.com/settings/personal-access-tokens → select it → **Delete**.

Why it matters: a fine-grained PAT scoped to `snappyai-backend` with
`contents: write` lets a holder **edit `builder.py`, `edsig.py` and
`entitlements.yml`**. Those run inside your GitHub Actions with
`STRIPE_SECRET_KEY` and `ED25519_SECRET` in their environment — so a single
commit that adds `echo "$ED25519_SECRET"` to the workflow hands over your
**entitlement signing key**, which means anyone can forge a valid
`entitlements.json` and grant themselves a subscription forever.

After revoking, also check:

```
https://github.com/gerykurucz/snappyai-backend/settings/secrets/actions   # anything rotated?
https://github.com/gerykurucz/snappyai-backend/actions                    # unfamiliar runs?
https://github.com/gerykurucz/snappyai-backend/commits                    # unfamiliar commits?
```

I did not use this token for anything, and it is not written to any file here.

---

## 2. Discord OAuth client secret — recoverable from your own source — **CRITICAL**

`build_secrets.py` "obfuscates" the blob with `XOR(sha256(_KEY))`, and `_KEY =
b"SnappyAI/build-secrets/v1"` is **in the same file**. I decoded it in seconds
without running your program. So `discord_client_secret()` is not protected —
it is recoverable by anyone with the source *or* the shipped exe.

**Rotate:** https://discord.com/developers/applications → your app → OAuth2 →
**Reset Secret**. Then update it everywhere it is deployed.

Your own docstring is honest about this ("obfuscated, not encrypted"), and
you're right that it's unavoidable for installed apps. But the fix isn't better
obfuscation — it's **not shipping the secret at all**: move the token exchange
behind an authenticated relay (the Worker could host it) so the client secret
never leaves your infrastructure. That removes this entire class of problem
instead of slowing it down. **Note: v14 does not do this yet** — in this
edition the exchange is still client-side, the rotated secret still lives in
`src/app/build_secrets.py` (`_BLOB["DISCORD_CLIENT_SEC"]`), and rotating it
still requires an exe rebuild. Server-side exchange is the recommended next
piece of work.

---

## 3. Discord presence webhook URL — recoverable the same way — **HIGH**

Also decoded. A webhook URL is a **bearer credential**: anyone holding it can
post to that channel indefinitely.

Consequences in your current design, which your own `online.md` comment block
already identifies precisely:

- Anyone can POST a second nonce for a victim's `identity_hash` and trip the
  `shared` flag → **remotely pause a paying customer's app**, repeatedly, free.
  Your `SHARED_CONFIRM_SNAPSHOTS = 2` mitigation raises the bar but does not
  close it: a sustained forgery still confirms after ~20 minutes.
- Channel spam, and webhook deletion as a denial-of-service on your detector.

**Revoke:** Discord → that channel → Integrations → Webhooks → **Delete**.

The permanent fix is what your own comment says it is — an authenticated relay
that only forwards beats carrying a valid per-install token (a future
`POST /api/v1/access/beat`-style endpoint). That is also what would let the
`shared` flag become **authoritative** rather than "corroborated evidence".
Not part of v14 — in this archive, shared-account handling stays
detection-only, and detection is dormant because the Worker does not scan the
presence channel (see `docs/ARCHITECTURE.md`).

---

## 4. `ROW_PEPPER` is empty — your customer list is crackable — **HIGH**

`describe_readiness()` already reports this as advisory:

> "no row-hash pepper - entitlement rows are keyed by unsalted sha256(e-mail) in a PUBLIC file"

`entitlements.json` lives in a **public** repo. Its keys are
`sha256("email:" + address)` with no pepper, so:

- The file publishes your **exact paying-customer count** to competitors.
- Anyone can run a dictionary over an email list (haveibeenpwned corpus, your
  Discord member list, a scraped user base) and **recover subscriber email
  addresses**. Email lists are sold; this is a GDPR-relevant exposure if any
  customer is in the EU/UK.

Adding a pepper helps but does not fix it: the pepper ships in the exe, so it
is recoverable, and the *count* is still public. The real fix is a design that
never publishes a customer list at all — each client receives a signed grant
containing **only its own row**. (Not part of v14; see the migration path in
`docs/ARCHITECTURE.md` — and remember `ROW_PEPPER` must stay EMPTY until the
Worker side changes too, or every customer is orphaned.)

---

## 5. Stripe payment links are in TEST mode — **HIGH (business, not security)**

Both `STRIPE_MONTHLY` and `STRIPE_TRIAL` decode to `buy.stripe.com/test_…`.

Your own `is_test_mode()` exists to catch exactly this: checkout appears to
succeed, **no money moves**, and no entitlement row is ever created. If a
frozen build shipped with these values, every "customer" since then has been
free and confused.

**Fix:** swap in the live-mode links, then confirm `describe_readiness()`
returns no advisories before your next build.

---

## 6. The Ed25519 signing key — ROTATED 2026-10-03

**Resolved by rotation.** A fresh Ed25519 key pair was generated on
2026-10-03; the new public key
(`J3Ulxeu/JPzIlGypJ28+h45rlw3aW6bJFfDu3luRGOE=`) is now pinned in
`worker/publisher-simple/source/src/worker.js` + the rebuilt bundle
`worker/publisher-simple/worker.js`, `worker/publisher-simple/source/wrangler.toml`,
and the client's `src/app/build_secrets.py`. The new secret seed is in
`docs/NEW-SIGNING-KEY.txt` — and it is **already saved** in the live Worker's
`ED25519_SECRET` (confirmed via `/healthz` on 2026-10-03), so that file is now
a recovery copy: delete it once you are confident, and never share the archive
with it inside.

The earlier worry below turned out to be a false alarm: the `_BLOB` value in
`build_secrets.py` is XOR-obfuscated, and decoding the old blob
(`ny66a9ZC...`) yields exactly the old workflow key
(`7Gext8qjCEKk0iYOor67Dd5BF+J9kulpjDATIgYsfxg=`). They were the same key all
along — the obfuscation just made them look different.

**Remaining actions after the rotation:**
1. ~~Save the new seed as `ED25519_SECRET`~~ **done** — but `/healthz` still
   shows `"pubkey_matches_expected": false` because the *deployed bundle* is
   the stale one; re-upload `worker/publisher-simple/worker.js`
   (`docs/WORKER-SETUP.md` Step 3) and it flips to `true`.
2. **Disable the old GitHub Actions builder** (private repo `snappyai-backend`,
   `*/10` cron). It still holds the OLD key and would overwrite
   `entitlements.json` with signatures that new clients reject.
3. Let the worker republish (hourly cron, or `POST /admin/publish`) so the live
   file is signed with the new key.
4. Rebuild and distribute the client exe with `src/app/` from this archive —
   installs carrying the old pin stop verifying after step 3, which is the
   expected, planned break this rotation accepts. (`docs/CLIENT-BUILD.md`.)

---

## Rotation checklist

| # | Credential | Where | Blocks shipping? |
|---|---|---|---|
| 1 | GitHub PAT | github.com → settings → PATs | **Yes** — signing key at risk |
| 2 | Discord OAuth client secret | discord.com/developers | Yes |
| 3 | Presence webhook URL | Discord channel → Integrations | Yes — paying customers can be paused remotely |
| 4 | `ROW_PEPPER` / public row keys | build config | Soon — customer list exposure |
| 5 | Stripe links → live mode | build config | **Yes** — you may not be getting paid |
| 6 | `ED25519_SECRET` | Worker secret (Cloudflare) | **DONE 2026-10-03** — saved in the live Worker; recovery copy in `docs/NEW-SIGNING-KEY.txt`; needs the bundle re-upload + a client rebuild |

Also worth doing while you're in there:

- `snappyai-backend`: Settings → Actions → General → **disable** any workflow
  you don't use, and confirm "Read and write permissions" is scoped as narrowly
  as the publisher allows.
- Enable **push protection** and **secret scanning** on both repos.
- Require PR reviews on `main` in the private repo — `builder.py` is a
  money-printing file and currently a single push away from being replaced.
- Check `snappyai-entitlements` is public **on purpose**. It must be, for
  `raw.githubusercontent.com` to be token-free — but that is precisely why
  item 4 matters.
