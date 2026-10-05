# src/app — the client side of SnappyAI

These are the Python files that ship inside the desktop app (the exe).
They are copied from your v8.27 client with exactly **one change**: the
pinned Ed25519 public key in `build_secrets.py` is the NEW key.

| File | Role |
|---|---|
| `online.py` | Sign-in (Discord OAuth), fetching + verifying `entitlements.json`, the subscription gate, presence pings |
| `edsig.py` | Dependency-free Ed25519 verify — checks the Worker's signature |
| `build_secrets.py` | All deployment constants (repo, pinned pubkey, Discord credentials, Stripe links), XOR-obfuscated |
| `gui.py` | The app window (unchanged) |
| `encode_secret.py` | Helper to re-encode a `_BLOB` value after a rotation (new in v14) |

## What is already set for you (do not edit)

In `build_secrets.py` → `_BLOB`:

- `ENTITLEMENT_PUBKEY` — decodes to the NEW pinned key
  `J3Ulxeu/JPzIlGypJ28+h45rlw3aW6bJFfDu3luRGOE=`
  (verify anytime: `python encode_secret.py --dump`)
- `ENTITLEMENT_REPO` — decodes to `gerykurucz/snappyai-entitlements`
- `ENTITLEMENT_BRANCH` — `live`
- `ROW_PEPPER` — **empty, and it must stay empty.** The Worker keys rows by
  unpeppered `sha256("email:" + address)`. Setting a pepper here would make
  the client look up rows the Worker never writes — every customer would be
  locked out. (A future pepper rollout needs a Worker change first; see
  `docs/ARCHITECTURE.md`.)

## Where the Discord secret goes

**`build_secrets.py` → `_BLOB["DISCORD_CLIENT_SEC"]` — here, in the client,
and NOWHERE else.** The Cloudflare Worker never sees it and has no variable
for it; the OAuth token exchange happens from the client (that is the current
design — see `docs/SECURITY-INCIDENT.md` item 2 for the trade-off).

After you reset the secret at
https://discord.com/developers/applications → your app → OAuth2 →
**Reset Secret**, encode the new value:

```
python encode_secret.py DISCORD_CLIENT_SEC "paste-the-new-secret-here"
```

and replace the `"DISCORD_CLIENT_SEC": "..."` line in `_BLOB` with the line
it prints. `DISCORD_CLIENT_ID` only changes if you create a whole new Discord
application.

## Known state of the other constants

- `STRIPE_MONTHLY` / `STRIPE_TRIAL` still decode to **test-mode**
  `buy.stripe.com/test_...` links. `is_test_mode()` flags this and a frozen
  build shows a loud advisory. Before taking real money, create live Payment
  Links in Stripe and re-encode them the same way.
- `PRESENCE_WEBHOOK` is set; shared-account detection stays detection-only.

## Rebuilding the exe

These four files **replace their counterparts in your full client source
tree** (the one with `main.py`, `config.py`, etc. — only these changed).
Copy them over, then run your normal build, e.g.:

```
pyinstaller --noconsole --onefile --name SnappyAI main.py
```

(plus whatever data files / hooks your usual build command already uses).
Full details and the pre-ship checklist: `docs/CLIENT-BUILD.md`.

## Self-check before you build

```
python -c "import build_secrets as b; f,a=b.describe_readiness(); print('FATAL:',f); print('ADVISORY:',a)"
```

Expect: `FATAL: []`, and two advisories (test-mode Stripe links, no row
pepper) — both known and intentional for now.
