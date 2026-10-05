# snappyai-entitlements

Machine-generated subscription feed for the SnappyAI desktop app.

- **`entitlements.json`** (branch **`live`**) is written automatically by a
  Cloudflare Worker every time Stripe reports a subscription event, and at
  least once per hour. **Do not edit it by hand** — the file carries an
  Ed25519 signature (`sig`); any manual edit invalidates it and every client
  will reject the file until the Worker republishes.
- The document is signed; clients pin the public key and fail closed if the
  signature does not verify or the file is older than 6 hours.
- Subscriber identities appear only as `sha256("email:" + address)` row keys —
  no plain-text e-mail addresses are stored here.

Clients fetch:

```
https://raw.githubusercontent.com/gerykurucz/snappyai-entitlements/live/entitlements.json
```
