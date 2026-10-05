#!/usr/bin/env bash
#
# Pre-flight checks for the SnappyAI publisher — v14 archive layout.
#
# Run it from anywhere:
#
#   bash tests/check-deploy.sh
#
# Layout it expects (archive root = the folder that contains tests/):
#
#   worker/publisher-simple/worker.js           the bundle you upload (dashboard)
#   worker/publisher-simple/source/             dev project (src/, wrangler.toml…)
#   src/app/                                    client-side Python (edsig.py …)
#   tests/                                      this script + the node tests
#
# It verifies: the bundle exists and is self-contained, carries the baked-in
# defaults (gerykurucz/snappyai-entitlements + the pinned NEW public key), has
# no editor-lighting patterns (require/msCrypto), is up to date with src/,
# exports fetch+scheduled, wrangler.toml is sane for the CLI route, and the
# whole node test suite passes (which includes cross-language verification
# with src/app/edsig.py — the client's own module).
set -uo pipefail

ok()   { printf '  \033[32mok\033[0m    %s\n' "$1"; }
bad()  { printf '  \033[31mFAIL\033[0m  %s\n' "$1"; FAILED=1; }
note() { printf '  \033[33m..\033[0m    %s\n' "$1"; }
FAILED=0

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/worker/publisher-simple/source"
BUNDLE="$ROOT/worker/publisher-simple/worker.js"
NEW_PUBKEY="J3Ulxeu/JPzIlGypJ28+h45rlw3aW6bJFfDu3luRGOE="
OLD_PUBKEY="7Gext8qjCEKk0iYOor67Dd5BF+J9kulpjDATIgYsfxg="

echo "== 1. archive layout ============================================="
echo "     root: $ROOT"
for f in "$BUNDLE" "$SRC/src/worker.js" "$SRC/wrangler.toml" "$ROOT/src/app/edsig.py" "$ROOT/src/app/build_secrets.py"; do
  if [ -f "$f" ]; then ok "${f#"$ROOT"/} present"; else bad "${f#"$ROOT"/} MISSING"; fi
done

echo
echo "== 2. wrangler.toml (CLI route only; dashboard ignores it) ======="
cd "$SRC" || exit 1
if grep -q '^main = "src/worker.js"' wrangler.toml; then
  ok "main points at src/worker.js"
else
  bad "main is missing or wrong -- wrangler will guess an entry point"
fi
if grep -q '^name = "publisher-simple"' wrangler.toml; then
  ok "worker name is publisher-simple (matches the LIVE worker URL)"
else
  bad "worker name is not publisher-simple -- \`wrangler deploy\` would create a SECOND worker"
  grep -n '^name' wrangler.toml
fi
if grep -qE '^[[:space:]]*(nodejs_compat|python_workers)[[:space:]]*=' wrangler.toml; then
  bad "found a bare compatibility key; flags must be an ARRAY"
else
  ok "no bogus boolean compatibility keys"
fi
if grep -q 'REPLACE_WITH_YOUR_BASE64_ED25519_PUBLIC_KEY' wrangler.toml; then
  bad "ED25519_EXPECTED_PUBKEY is still the placeholder"
elif grep -q "$NEW_PUBKEY" wrangler.toml; then
  ok "ED25519_EXPECTED_PUBKEY is the NEW pinned key"
else
  bad "ED25519_EXPECTED_PUBKEY is not the new key ($NEW_PUBKEY)"
fi
if grep -q "$OLD_PUBKEY" wrangler.toml; then
  bad "wrangler.toml still mentions the OLD (rotated-away) public key"
fi
if grep -qE '^\[\[(d1_databases|kv_namespaces)\]\]' wrangler.toml; then
  note "wrangler.toml declares a D1/KV binding -- this edition needs neither"
else
  ok "no database binding (correct: storage is one JSON file in the public repo)"
fi

echo
echo "== 3. dependencies ==============================================="
# tweetnacl is VENDORED, not installed. The npm package is CommonJS-only, so an
# ES-module Worker cannot resolve a bare import of it.
if [ -f src/vendor/tweetnacl.js ]; then
  ok "tweetnacl vendored at src/vendor/tweetnacl.js"
else
  bad "src/vendor/tweetnacl.js missing -- signing cannot work"
fi
if [ -f src/vendor/LICENSE-tweetnacl ]; then
  ok "vendored licence retained (Unlicense)"
else
  note "src/vendor/LICENSE-tweetnacl missing -- keep the upstream licence file"
fi
BARE=$(grep -rnE '^import[[:space:]].*[[:space:]]from[[:space:]]*"[^./]' src/ 2>/dev/null || true)
if [ -n "$BARE" ]; then
  bad "src/ has a bare (non-relative) import -- a Worker cannot resolve it:"
  printf '%s\n' "$BARE" | sed 's/^/          /'
else
  ok "every import in src/ is a relative path (nothing to resolve at runtime)"
fi

echo
echo "== 4. entry point parses as an ES module ========================="
if node --input-type=module -e "import('$SRC/src/worker.js').then(m=>{if(typeof m.default?.fetch!=='function')throw new Error('no default.fetch export');console.log('default.fetch exported')})" 2>/dev/null; then
  ok "src/worker.js exports a default fetch handler"
else
  bad "src/worker.js does not export a usable default.fetch"
fi

echo
echo "== 5. dashboard single-file bundle ==============================="
# The dashboard upload flow ignores wrangler.toml and src/ and only runs a root
# worker.js, so worker/publisher-simple/worker.js is the real production
# artifact for that route. It must exist, be self-contained, and carry the
# baked-in defaults.
if [ ! -f "$BUNDLE" ]; then
  bad "worker/publisher-simple/worker.js missing -- rebuild it: (cd $SRC && npm install && node build-bundle.mjs)"
else
  ok "worker/publisher-simple/worker.js exists (the single file you upload in the dashboard)"
  if grep -qE '^[[:space:]]*import[[:space:]].*from' "$BUNDLE"; then
    bad "the bundle still has import statements -- not self-contained"
  else
    ok "the bundle is self-contained (no imports)"
  fi
  if grep -q 'gerykurucz/snappyai-entitlements' "$BUNDLE" && grep -q 'J3Ulxeu/JPzIlGypJ28' "$BUNDLE"; then
    ok "baked-in defaults (repo + NEW pinned pubkey) present in the bundle"
  else
    bad "bundle is missing baked-in defaults -- rebuild: node build-bundle.mjs"
  fi
  if grep -q "$OLD_PUBKEY" "$BUNDLE"; then
    bad "bundle still contains the OLD rotated-away pubkey -- it is STALE, rebuild it"
  else
    ok "no trace of the old pubkey in the bundle"
  fi
  # The Cloudflare dashboard editor type-checks the uploaded file. Upstream
  # tweetnacl's ES5 idioms (a dead Node `require` branch, the IE `msCrypto`
  # probe) light it up with false-positive errors. The vendored copy is
  # patched, so the bundle must contain NONE of these patterns.
  if grep -qE '__require|msCrypto|\brequire\(' "$BUNDLE"; then
    bad "bundle contains require/__require/msCrypto -- the vendored tweetnacl"
    echo "       patches were lost. The dashboard editor will show false errors."
    grep -nE '__require|msCrypto|\brequire\(' "$BUNDLE" | head -5 | sed 's/^/          /'
  else
    ok "no require/__require/msCrypto in the bundle (dashboard editor stays clean)"
  fi
  if head -1 "$BUNDLE" | grep -q '@ts-nocheck'; then
    ok "@ts-nocheck banner present (silences editor diagnostics on generated code)"
  else
    note "@ts-nocheck banner missing -- editor may show squiggles on generated code"
  fi
  if [ -x node_modules/.bin/tsc ] && [ -f tsconfig.editorcheck.json ]; then
    if node_modules/.bin/tsc -p tsconfig.editorcheck.json >/tmp/check-deploy-tsc.log 2>&1; then
      ok "editor type-check (tsc + @cloudflare/workers-types): 0 problems"
    else
      bad "editor type-check FAILED -- the dashboard will show red squiggles:"
      head -10 /tmp/check-deploy-tsc.log | sed 's/^/          /'
    fi
  else
    note "typescript not installed -- skipping editor type-check (cd source && npm install to enable)"
  fi
  BUNDLE_OLDER=$(find src build-bundle.mjs -newer "$BUNDLE" 2>/dev/null | head -3)
  if [ -n "$BUNDLE_OLDER" ]; then
    bad "src/ changed AFTER the bundle was built -- worker.js is stale:"
    printf '%s\n' "$BUNDLE_OLDER" | sed 's/^/          /'
    echo "       rebuild: npm install && node build-bundle.mjs"
  else
    ok "bundle is up to date with src/"
  fi
  if node --input-type=module -e "import('$BUNDLE').then(m=>{if(typeof m.default?.fetch!=='function'||typeof m.default?.scheduled!=='function')throw new Error('missing handlers')})" 2>/dev/null; then
    ok "the bundle exports fetch + scheduled handlers"
  else
    bad "the bundle does not load as a usable Worker module"
  fi
fi

echo
echo "== 6. client-side pin (src/app/build_secrets.py) ================="
if command -v python3 >/dev/null 2>&1; then
  PIN_CHECK=$(python3 - "$ROOT/src/app/build_secrets.py" "$NEW_PUBKEY" <<'PYEOF'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("bs", sys.argv[1])
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)
want = sys.argv[2]
got = bs.entitlement_pubkey()
repo = bs.entitlement_repo()
branch = bs.entitlement_branch()
ok = (got == want) and (repo == "gerykurucz/snappyai-entitlements") and (branch == "live")
print(("ok    pin=%s repo=%s branch=%s" % (got, repo, branch)) if ok
      else ("FAIL  pin=%s (want %s) repo=%s branch=%s" % (got, want, repo, branch)))
sys.exit(0 if ok else 1)
PYEOF
  ) && ok "build_secrets.py decodes to the NEW pubkey + gerykurucz/snappyai-entitlements@live" \
    || bad "build_secrets.py pin check failed: $PIN_CHECK"
else
  note "python3 not found -- skipping the client pin decode check"
fi

echo
echo "== 7. tests ======================================================="
cd "$ROOT" || exit 1
if node --test tests/ >/tmp/check-deploy-tests.log 2>&1; then
  ok "$(grep -E '^# (pass|tests)' /tmp/check-deploy-tests.log | tr '\n' ' ')"
else
  bad "tests failing:"
  grep -E '^# (pass|fail)|^not ok' /tmp/check-deploy-tests.log | head -10 | sed 's/^/          /'
fi

echo
if [ "$FAILED" -eq 0 ]; then
  echo "All clear. Deploy by uploading worker/publisher-simple/worker.js in the"
  echo "Cloudflare dashboard (or: cd worker/publisher-simple/source && wrangler deploy)."
  echo "Then follow docs/START-HERE.md."
else
  echo "Fix the FAIL items above, then re-run this script."
fi
exit $FAILED
