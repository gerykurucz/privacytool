# Client build — shipping the exe with the NEW key

The four client files in `src/app/` are your v8.27 sources with exactly one
functional change: `_BLOB["ENTITLEMENT_PUBKEY"]` in `build_secrets.py` now
encodes the NEW key `J3Ulxeu/JPzIlGypJ28+h45rlw3aW6bJFfDu3luRGOE=`.
(`encode_secret.py` is a new helper and is not imported by the app.)

## 1. Drop the files into your client source tree

Copy these over the same-named files in your full client project (the one
with `main.py`, `config.py`, …):

```
src/app/online.py
src/app/edsig.py
src/app/gui.py
src/app/build_secrets.py
```

Nothing else in the client changes. It keeps fetching the same URL:

```
https://raw.githubusercontent.com/gerykurucz/snappyai-entitlements/live/entitlements.json
```

## 2. Rotate the Discord client secret FIRST (recommended)

The old secret is recoverable from the old source in seconds
(`SECURITY-INCIDENT.md` item 2). Since you must rebuild the exe anyway for
the new key, rotate now:

1. https://discord.com/developers/applications → your app → OAuth2 →
   **Reset Secret** → copy the new value
2. In `src/app/`:
   ```
   python encode_secret.py DISCORD_CLIENT_SEC "paste-the-new-secret"
   ```
3. Replace the `"DISCORD_CLIENT_SEC": "…"` line in `_BLOB` with the printed
   line.

The Discord secret lives **only** here — never in the Worker, never in
config.json (`SENSITIVE_KEYS` blocks that), never in chat.

## 3. Self-check the constants

```
cd src/app
python encode_secret.py --dump
python -c "import build_secrets as b; f,a=b.describe_readiness(); print('FATAL:',f); print('ADVISORY:',a)"
```

Expect:

- `ENTITLEMENT_PUBKEY = J3Ulxeu/JPzIlGypJ28+h45rlw3aW6bJFfDu3luRGOE=`
- `ENTITLEMENT_REPO   = gerykurucz/snappyai-entitlements`, branch `live`
- `FATAL: []`
- `ADVISORY:` test-mode Stripe links + no row pepper — **both known and
  intentional right now** (pepper must stay empty; see `SECRET-MAP.md`).

## 4. Build

Your normal command, e.g.:

```
pyinstaller --noconsole --onefile --name SnappyAI main.py
```

## 5. Smoke-test before distributing

1. Start the exe, sign in with a Discord account that has an active row
   (after `WORKER-SETUP.md` Step 7 you can create one with a Stripe test
   checkout, or grant yourself time via `POST /admin/grant`).
2. The app must pass the gate: file fetches, signature verifies under the
   new pin, row found. If it says the file is stale, wait for the hourly
   cron or force `POST /admin/publish`.
3. Negative test: temporarily rename the repo file (or point a dev override
   `SNAPPYAI_ENT_REPO` at a scratch repo with a hand-edited JSON) and confirm
   the app **fails closed** — a tampered file must never pass.

## 6. Distribute — and know what breaks

- **Installs built from the OLD source (old pinned key) stop verifying the
  file as soon as the Worker publishes a new-key signature.** That is the
  planned break of the key rotation; the fix for those users is this new exe.
- Announce/serve the update before (or immediately after) the Worker goes
  live, or old installs will show "no subscription" for everyone.

## Later, before taking real money

- Replace `STRIPE_MONTHLY` / `STRIPE_TRIAL` with **live** Payment Links
  (encode with `encode_secret.py`), and confirm `is_test_mode()` is False via
  the Step-3 check — a frozen build shows a loud advisory otherwise.
- Recreate the presence webhook (`SECURITY-INCIDENT.md` item 3) and re-encode
  `PRESENCE_WEBHOOK`.
