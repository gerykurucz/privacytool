/**
 * Tests for worker/publisher-simple/worker.js — the GENERATED single-file build.
 *
 * The dashboard upload flow ignores wrangler.toml and src/, so what actually
 * runs in production is this one file. These tests drive THAT file (not src/)
 * through a full webhook → publish cycle, and verify the output with the
 * client's own unmodified edsig.py. If the bundle ever drifts from src/ or
 * esbuild breaks the vendored tweetnacl, this fails before the user finds out
 * in front of a customer.
 *
 *     npm test
 */

import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { createHmac } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import test from "node:test";

import { publicKeyB64, verifyDocument } from "../worker/publisher-simple/source/src/signing.js";
import { rowKey } from "../worker/publisher-simple/source/src/entitlements.js";
import bundle from "../worker/publisher-simple/worker.js";
import { createFakeGithub } from "./github-stub.js";

const DAY = 86_400;
const SEED_HEX = "22".repeat(32); // deliberately different from publisher.test.js
const PUB = publicKeyB64(SEED_HEX);
const SECRET = "whsec_bundle_test";
const EMAIL = "bundle-customer@example.com";
const PINNED = "J3Ulxeu/JPzIlGypJ28+h45rlw3aW6bJFfDu3luRGOE=";
const BUNDLE_PATH = new URL("../worker/publisher-simple/worker.js", import.meta.url);

const realFetch = globalThis.fetch;
let gh = null;

function installGithub(initial = null) {
  gh = createFakeGithub(initial);
  globalThis.fetch = gh.fetch;
  return gh;
}

/** Secrets only — NO PUBLIC_REPO / BRANCH / FILE_PATH / EXPECTED_PUBKEY vars,
 *  exactly like a dashboard upload where the user only added secrets. */
function secretsOnlyEnv(overrides = {}) {
  return {
    ED25519_SECRET: SEED_HEX,
    STRIPE_WEBHOOK_SIGNING_SECRET: SECRET,
    GITHUB_PAT: "github_pat_fake",
    ADMIN_TOKEN: "admin-token",
    ...overrides,
  };
}

const CTX = { waitUntil: (p) => p };

function signedRequest(event, secret = SECRET, ts = Math.floor(Date.now() / 1000)) {
  const body = JSON.stringify(event);
  const digest = createHmac("sha256", secret).update(`${ts}.${body}`).digest("hex");
  return new Request("https://pub.example.com/webhooks/stripe", {
    method: "POST",
    body,
    headers: { "stripe-signature": `t=${ts},v1=${digest}`, "content-type": "application/json" },
  });
}

function basilCheckout(periodEnd, email = EMAIL) {
  return {
    id: `evt_bundle_${periodEnd}`,
    type: "checkout.session.completed",
    created: Math.floor(Date.now() / 1000),
    data: {
      object: {
        customer_email: email,
        subscription: {
          id: "sub_bundle",
          status: "active",
          items: { data: [{ current_period_end: periodEnd }] },
        },
      },
    },
  };
}

test.beforeEach(() => installGithub());
test.afterEach(() => {
  globalThis.fetch = realFetch;
});

// ---------------------------------------------------------------------------
// The artifact itself
// ---------------------------------------------------------------------------

test("the bundle is a single self-contained file (no imports, no require)", () => {
  const text = readFileSync(BUNDLE_PATH, "utf-8");
  assert.ok(text.length > 10_000, "bundle suspiciously small");
  // ESM import/export statements would break the dashboard's single-file flow.
  assert.equal(/^\s*import\s.+from\s/m.test(text), false, "bundle still has an import statement");
  assert.equal(/^\s*export\s(?!\{)/m.test(text.replace(/export default/, "")), false);
  assert.equal(/\brequire\s*\(/.test(text), false, "bundle still has a require() call");
  assert.ok(text.includes("GENERATED FILE"), "banner missing — is this really the built bundle?");
  // Baked-in defaults must survive bundling.
  assert.ok(text.includes("gerykurucz/snappyai-entitlements"), "repo default missing from bundle");
  assert.ok(text.includes(PINNED), "pinned pubkey default missing from bundle");
});

test("the bundle exports fetch and scheduled handlers", () => {
  assert.equal(typeof bundle.fetch, "function");
  assert.equal(typeof bundle.scheduled, "function");
});

// ---------------------------------------------------------------------------
// Runtime behaviour with a dashboard-style env (secrets only, zero vars)
// ---------------------------------------------------------------------------

test("/healthz reports the baked-in state-file location with zero vars set", async () => {
  installGithub(null);
  const resp = await bundle.fetch(
    new Request("https://pub.example.com/healthz"),
    secretsOnlyEnv(),
    CTX
  );
  assert.equal(resp.status, 200);
  const body = await resp.json();
  assert.equal(body.state_file, "gerykurucz/snappyai-entitlements/entitlements.json@live");
  assert.equal(body.service, "snappyai-entitlement-publisher");
  // The GitHub calls must have gone to the baked-in repo.
  assert.ok(gh.calls.every((c) => c.url.includes("gerykurucz/snappyai-entitlements")));
});

test("a full Stripe webhook through the BUNDLE publishes a row the client can verify", async () => {
  installGithub(null);
  const end = Math.floor(Date.now() / 1000) + 30 * DAY;
  const resp = await bundle.fetch(
    signedRequest(basilCheckout(end)),
    // Override only the pubkey pin: the test seed is not the production key.
    secretsOnlyEnv({ ED25519_EXPECTED_PUBKEY: PUB }),
    CTX
  );
  assert.equal(resp.status, 200, await resp.clone().text());
  const body = await resp.json();
  assert.equal(body.applied, true, JSON.stringify(body));
  assert.equal(body.published, true);

  const doc = gh.content;
  const hash = await rowKey(EMAIL);
  assert.equal(doc.rows[hash].status, "active");
  assert.equal(doc.rows[hash].until, end);
  assert.equal(verifyDocument(doc, PUB), true);

  // And the real cross-language check: the client's UNMODIFIED edsig.py must
  // accept the exact bytes the bundle published.
  writeFileSync(
    "/tmp/bundle-interop.json",
    JSON.stringify({ pubkey_b64: PUB, seed_hex: SEED_HEX, signed_doc: doc })
  );
  const script = new URL("./verify-with-edsig.py", import.meta.url).pathname;
  const out = execFileSync("python3", [script, "/tmp/bundle-interop.json"], { encoding: "utf-8" });
  assert.match(out, /^ALL OK/m, `edsig.py rejected the bundle's published file:\n${out}`);
});

test("the bundle refuses to sign when the seed does not match the PINNED production key", async () => {
  // This is the dashboard foot-gun the baked-in default is there to catch:
  // secrets only, no EXPECTED_PUBKEY var → the pin from the bundle applies,
  // and a wrong/rotated seed must fail LOUDLY, never publish a bad file.
  installGithub(null);
  const end = Math.floor(Date.now() / 1000) + 30 * DAY;
  const resp = await bundle.fetch(
    signedRequest(basilCheckout(end)),
    secretsOnlyEnv(), // no override: PINNED applies, but SEED_HEX ≠ production seed
    CTX
  );
  assert.equal(resp.status, 500);
  const body = await resp.json();
  assert.match(body.error, /does not match|Refusing to sign|expected/i);
  assert.equal(gh.putCalls().length, 0, "nothing may be published with a mismatched key");
});

test("cron scheduled() republishes through the bundle", async () => {
  installGithub(null);
  // First, get a document published (with a matching pin override).
  const end = Math.floor(Date.now() / 1000) + 30 * DAY;
  await bundle.fetch(
    signedRequest(basilCheckout(end)),
    secretsOnlyEnv({ ED25519_EXPECTED_PUBKEY: PUB }),
    CTX
  );
  assert.equal(gh.putCalls().length, 1);

  // Then let the hourly keepalive run. scheduled() fire-and-forgets through
  // ctx.waitUntil, so capture the promise and await it.
  let pending = null;
  const captureCtx = { waitUntil: (p) => (pending = p) };
  await bundle.scheduled({}, secretsOnlyEnv({ ED25519_EXPECTED_PUBKEY: PUB }), captureCtx);
  await pending;

  assert.equal(gh.putCalls().length, 2, "keepalive did not rewrite the file");
  assert.equal(verifyDocument(gh.content, PUB), true);
  assert.equal(gh.content.rows[await rowKey(EMAIL)].status, "active");
});
