# How to create the public repo (browser only, ~5 minutes)

Everything inside the `snappyai-entitlements/` folder next to this file is
**exactly what goes into the public GitHub repo** — nothing else, nothing less.

> **Already have the repo?** If `github.com/gerykurucz/snappyai-entitlements`
> still exists with an `entitlements.json` on branch `live`, you can skip this
> entirely. The Worker reads the existing file, keeps every `rows` entry, and
> re-signs it with the NEW key on its first publish. Old signatures are simply
> replaced. (The old GitHub Actions builder must be disabled — see
> `docs/NEW-SIGNING-KEY.txt`, section 4.)

## Step 1 — create the repo

1. Go to https://github.com/new
2. Repository name: `snappyai-entitlements`
3. Owner: `gerykurucz`
4. Visibility: **Public**  ← must be public; clients fetch it without a token
5. Tick **Add a README file**
6. Click **Create repository**

## Step 2 — create the `live` branch

1. In the new repo, click the branch button (top left, says `main`)
2. Type `live` in the box
3. Click **Create branch: live**

## Step 3 — upload the two files

Stay on the `live` branch (the branch button must say `live`):

1. Click **Add file → Upload files**
2. Drag in **both** files from the `snappyai-entitlements/` folder:
   - `entitlements.json`  (the placeholder — the Worker replaces it, signed, on first publish)
   - `README.md`          (tick "replace" if GitHub asks — it replaces the auto-created one)
3. Scroll down, make sure **Commit directly to the `live` branch** is selected
4. Click **Commit changes**

## Step 4 — check the URL the client uses

Open this exact URL in your browser:

```
https://raw.githubusercontent.com/gerykurucz/snappyai-entitlements/live/entitlements.json
```

You must see:

```json
{"v": 1, "generated_at": 0, "cursor": 0, "rows": {}}
```

If you see that, the repo side is done. Continue with
`docs/WORKER-SETUP.md` (GitHub token + Cloudflare secrets).

---

### Why a placeholder and not a signed file?

`generated_at: 0` is the marker the Worker looks for
(`isPlaceholder` in the source): it tells the Worker "fresh repo, start from
scratch". On its first publish — the first Stripe webhook, an admin call, or
the hourly cron, whichever comes first — the Worker replaces this file with a
real document signed with the new Ed25519 key. Until then, clients fail
closed (they show "no subscription yet"), which is correct: nobody has one.
