/**
 * Tests for the no-database publisher.
 *
 *     npm test
 *
 * Storage is one JSON file in a public repo, so the two things that matter most
 * are: (1) the state machine behaves exactly like builder.py, and (2) the
 * published bytes verify under the client's own edsig.py. Both are checked here;
 * (2) is checked for real by shelling out to test/verify-with-edsig.py, which
 * imports the UNMODIFIED edsig.py from the client tree.
 */

import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { createHmac } from "node:crypto";
import { writeFileSync } from "node:fs";
import test from "node:test";

import {
  applyEventToRow,
  bindSubscription,
  buildDocument,
  cancel,
  checkRowFloor,
  extractEmail,
  extractPeriodEnd,
  grantTrial,
  isActive,
  markRefunded,
  recompute,
  rowKey,
  supportGrant,
  syncSubscription,
} from "../worker/publisher-simple/source/src/entitlements.js";
import { publicKeyB64, signDocument, verifyDocument } from "../worker/publisher-simple/source/src/signing.js";
import {
  emptyState,
  hasSeen,
  markSeen,
  prune,
  readState,
  rememberIds,
  resolveHash,
  subscriptionIdOf,
  toPublicRows,
  trimSeen,
  writeState,
} from "../worker/publisher-simple/source/src/state-file.js";
import worker from "../worker/publisher-simple/source/src/worker.js";
import { createFakeGithub } from "./github-stub.js";

const NOW = 1_800_000_000;
const DAY = 86_400;
const SEED_HEX = "11".repeat(32);
const PUB = publicKeyB64(SEED_HEX);
const SECRET = "whsec_publisher_test";
const EMAIL = "customer@example.com";

// ---------------------------------------------------------------------------
// harness
// ---------------------------------------------------------------------------
const realFetch = globalThis.fetch;
let gh = null;

function installGithub(initial = null) {
  gh = createFakeGithub(initial);
  globalThis.fetch = gh.fetch;
  return gh;
}

function env(overrides = {}) {
  return {
    ED25519_SECRET: SEED_HEX,
    ED25519_EXPECTED_PUBKEY: PUB,
    STRIPE_WEBHOOK_SIGNING_SECRET: SECRET,
    GITHUB_PAT: "github_pat_fake",
    ADMIN_TOKEN: "admin-token",
    PUBLIC_REPO: "gerykurucz/snappyai-entitlements",
    BRANCH: "live",
    FILE_PATH: "entitlements.json",
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

/** A Basil-shaped event: period end on items.data, NOT at the top level. */
function basilEvent(type, periodEnd, email = EMAIL, id) {
  return {
    id: id || `evt_${type}_${periodEnd}`,
    type,
    created: Math.floor(Date.now() / 1000),
    data: {
      object: {
        customer_email: email,
        subscription: {
          id: "sub_demo",
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
// state machine — must match builder.py
// ---------------------------------------------------------------------------
test("recompute derives active from until AND status", () => {
  assert.equal(recompute({ status: "active", until: NOW + DAY }, NOW).active, true);
  assert.equal(recompute({ status: "active", until: NOW - DAY }, NOW).active, false);
  assert.equal(recompute({ status: "canceled", until: NOW + DAY }, NOW).active, false);
  assert.equal(recompute({ status: "canceling", until: NOW + DAY }, NOW).active, true);
});

test("a trial does not downgrade a paid month, a canceling month or a grant", () => {
  const paid = bindSubscription({ status: "unsubscribed", until: 0 }, NOW, NOW + 30 * DAY, "active", "sub_1");
  assert.equal(grantTrial(paid, NOW).status, "active");
  for (const status of ["canceling", "grant"]) {
    const row = recompute({ status, plan: "monthly", until: NOW + 10 * DAY }, NOW);
    assert.equal(grantTrial(row, NOW).status, status);
  }
});

test("a refund is only un-revoked by a NEWER checkout", () => {
  let row = bindSubscription({ status: "unsubscribed", until: 0 }, NOW, NOW + 30 * DAY, "active", "sub_1");
  row = markRefunded(row, NOW + 10);
  assert.equal(bindSubscription(row, NOW - 100, NOW + 30 * DAY, "active", "sub_1").status, "refunded");
  assert.equal(bindSubscription(row, NOW + 1000, NOW + 1030 * DAY, "active", "sub_2").status, "active");
});

test("cancel_at_period_end keeps access to the paid period end", () => {
  const end = NOW + 20 * DAY;
  let row = bindSubscription({ status: "unsubscribed", until: 0 }, NOW, end, "active", "sub_1");
  row = syncSubscription(row, NOW + 5, end, "active", true);
  assert.equal(row.status, "canceling");
  assert.equal(row.until, end);
  assert.equal(row.active, true);
});

test("subscription.deleted revokes immediately", () => {
  const row = bindSubscription({ status: "unsubscribed", until: 0 }, NOW, NOW + 30 * DAY, "active", "sub_1");
  const after = cancel(row, NOW + 100);
  assert.equal(after.status, "canceled");
  assert.equal(after.active, false);
});

test("a successful payment clears past_due", () => {
  const row = recompute({ status: "past_due", plan: "monthly", until: NOW + 30 * DAY }, NOW);
  const after = applyEventToRow(
    row,
    { type: "invoice.paid", data: { object: { subscription: { id: "s", current_period_end: NOW + 30 * DAY } } } },
    NOW,
    NOW
  );
  assert.equal(after.status, "active");
});

test("period end is read from items on Basil-shaped events", () => {
  const end = NOW + 30 * DAY;
  const sub = { id: "s", items: { data: [{ current_period_end: end }] } };
  assert.equal(sub.current_period_end, undefined, "precondition");
  assert.equal(extractPeriodEnd({ data: { object: {} } }, sub), end);
  assert.equal(extractPeriodEnd({ data: { object: {} } }, { id: "s", current_period_end: end }), end);
  assert.equal(extractPeriodEnd({ data: { object: { lines: { data: [{ period: { end } }] } } } }, { id: "s" }), end);
});

test("email is found in every shape Stripe uses", () => {
  for (const [i, key] of ["customer_email", "receipt_email", "billing_email"].entries()) {
    const event = { data: { object: { [key]: `user${i}@example.com` } } };
    assert.equal(extractEmail(event), `user${i}@example.com`);
  }
  assert.equal(extractEmail({ data: { object: { customer_details: { email: "x@y.z" } } } }), "x@y.z");
  assert.equal(extractEmail({ data: { object: {} } }), null);
});

test("row key is byte-identical to builder.row_key()", async () => {
  const { createHash } = await import("node:crypto");
  const expected = createHash("sha256").update("email:customer@example.com").digest("hex");
  assert.equal(await rowKey("  Customer@Example.COM "), expected);
});

// ---------------------------------------------------------------------------
// state file
// ---------------------------------------------------------------------------
test("readState on an empty repo returns a fresh state and no sha", async () => {
  installGithub(null);
  const { doc, sha, missing } = await readState({
    PUBLIC_REPO: "a/b",
    BRANCH: "live",
    FILE_PATH: "entitlements.json",
    GITHUB_PAT: "tok",
  });
  assert.equal(missing, true);
  assert.equal(sha, null);
  assert.deepEqual(doc.rows, {});
});

test("readState replaces the shipped placeholder rather than trusting it", async () => {
  installGithub(JSON.stringify({ v: 1, generated_at: 0, cursor: 0, rows: {}, sig: "" }));
  const { doc, sha } = await readState({
    PUBLIC_REPO: "a/b", BRANCH: "live", FILE_PATH: "entitlements.json", GITHUB_PAT: "tok",
  });
  assert.ok(doc.generated_at > 0, "the placeholder's generated_at=0 is replaced with a real clock");
  assert.deepEqual(doc.rows, {});
  assert.ok(sha, "sha is kept so the write is still a compare-and-swap");
});

test("readState refuses to proceed on a corrupt file", async () => {
  installGithub("{ this is not json");
  await assert.rejects(
    readState({ PUBLIC_REPO: "a/b", BRANCH: "live", FILE_PATH: "entitlements.json", GITHUB_PAT: "tok" }),
    /not valid JSON/
  );
});

test("writeState with a stale sha reports a conflict instead of overwriting", async () => {
  const g = installGithub(JSON.stringify({ v: 1, generated_at: 1, rows: {} }));
  const cfg = { PUBLIC_REPO: "a/b", BRANCH: "live", FILE_PATH: "entitlements.json", GITHUB_PAT: "tok" };
  const { sha } = await readState(cfg);

  g.setExternally(JSON.stringify({ v: 1, generated_at: 2, rows: { someone: {} } }));
  const result = await writeState(cfg, '{"v":1}', sha, "stale write");
  assert.equal(result.ok, false);
  assert.equal(result.conflict, true, "a stale write must conflict, not clobber");
  assert.equal(g.content.generated_at, 2, "the concurrent writer's content survived");
});

test("seen is bounded, so the file cannot grow forever", () => {
  let state = emptyState(NOW);
  for (let i = 0; i < 900; i++) state = markSeen(state, `evt_${i}`);
  assert.equal(state.seen.length, 500);
  assert.ok(state.seen.includes("evt_899"), "newest must be kept");
  assert.ok(!state.seen.includes("evt_0"), "oldest must be dropped");
  assert.equal(hasSeen(state, "evt_899"), true);
  assert.equal(hasSeen(state, "evt_0"), false);
});

test("prune drops dead rows and the ids pointing at them", () => {
  const state = emptyState(NOW);
  state.rows = {
    live: { status: "active", until: NOW + DAY },
    dead: { status: "canceled", until: NOW - 200 * DAY },
  };
  state.subs = { sub_live: "live", sub_dead: "dead" };
  state.pis = { pi_dead: "dead" };
  prune(state, NOW, 90 * DAY);
  assert.deepEqual(Object.keys(state.rows), ["live"]);
  assert.deepEqual(Object.keys(state.subs), ["sub_live"]);
  assert.deepEqual(Object.keys(state.pis), []);
});

test("all three Stripe subscription-id shapes are recognised", () => {
  // invoice.paid: expanded Subscription object
  assert.equal(subscriptionIdOf({ data: { object: { subscription: { id: "sub_a" } } } }), "sub_a");
  // checkout.session.completed: bare id string
  assert.equal(subscriptionIdOf({ data: { object: { subscription: "sub_b" } } }), "sub_b");
  // customer.subscription.*: the object IS the subscription
  assert.equal(subscriptionIdOf({ data: { object: { id: "sub_c", object: "subscription" } } }), "sub_c");
  // and a non-subscription object id is not mistaken for one
  assert.equal(subscriptionIdOf({ data: { object: { id: "cus_1", object: "customer" } } }), null);
  assert.equal(subscriptionIdOf({ data: { object: {} } }), null);
});

test("resolveHash finds a row by subscription id when the email is absent", () => {
  const state = emptyState(NOW);
  state.subs = { sub_1: "hash_1" };
  assert.equal(resolveHash(state, { data: { object: { subscription: "sub_1" } } }, null), "hash_1");
  assert.equal(resolveHash(state, { data: { object: { subscription: { id: "sub_1" } } } }, null), "hash_1");
  assert.equal(resolveHash(state, { data: { object: { id: "sub_1" } } }, null), "hash_1",
    "customer.subscription.deleted carries the id on the object itself");
  assert.equal(resolveHash(state, { data: { object: { payment_intent: "pi_9" } } }, null), null);
});

test("rememberIds records the subscription and payment-intent mapping", () => {
  const state = emptyState(NOW);
  rememberIds(state, { data: { object: { subscription: { id: "sub_x" }, payment_intent: "pi_x" } } }, "hash_x");
  assert.equal(state.subs.sub_x, "hash_x");
  assert.equal(state.pis.pi_x, "hash_x");
});

test("toPublicRows keeps the fields the state machine needs on re-read", () => {
  const state = emptyState(NOW);
  state.rows = {
    aaa: { status: "active", plan: "monthly", until: NOW + 30 * DAY, refunded_at: 0, sub_id: "s" },
    bbb: { status: "refunded", plan: null, until: NOW, refunded_at: NOW - 10, shared: true, note: "why" },
  };
  const rows = toPublicRows(state);

  assert.deepEqual(Object.keys(rows.aaa).sort(), ["plan", "refunded_at", "status", "until"]);
  assert.equal(typeof rows.aaa.until, "number");
  assert.equal(rows.aaa.sub_id, undefined, "sub_id stays out of the public file");

  // The regression this pins: refunded_at must survive a publish/read cycle,
  // or a replayed older checkout can resurrect a refunded subscription.
  assert.equal(rows.bbb.refunded_at, Math.trunc(NOW - 10));
  assert.equal(rows.bbb.shared, true);
  assert.equal(rows.bbb.note, "why");
});

test("a refund survives a republish and still blocks resurrection", async () => {
  installGithub(null);
  const e = env();
  const end = Math.floor(Date.now() / 1000) + 30 * DAY;
  const hash = await rowKey(EMAIL);

  await worker.fetch(signedRequest(basilEvent("checkout.session.completed", end, EMAIL, "evt_p1")), e, CTX);
  await worker.fetch(
    signedRequest({
      id: "evt_p2",
      type: "charge.refunded",
      created: Math.floor(Date.now() / 1000) + 10,
      data: { object: { customer_email: EMAIL } },
    }),
    e,
    CTX
  );
  assert.equal(gh.content.rows[hash].status, "refunded");
  const refundedAt = gh.content.rows[hash].refunded_at;
  assert.ok(refundedAt > 0, "refunded_at must be persisted in the published file");

  // Force a full re-read from the published file, then replay an OLDER checkout.
  const replay = basilEvent("checkout.session.completed", end, EMAIL, "evt_p3");
  replay.created = Math.floor(Date.now() / 1000) - 100;
  await worker.fetch(signedRequest(replay), e, CTX);
  assert.equal(gh.content.rows[hash].status, "refunded", "a replayed older checkout resurrected a refund");
});

test("the shared flag survives a payment event", async () => {
  installGithub(null);
  const e = env();
  const end = Math.floor(Date.now() / 1000) + 30 * DAY;
  const hash = await rowKey(EMAIL);

  await worker.fetch(signedRequest(basilEvent("checkout.session.completed", end, EMAIL, "evt_s1")), e, CTX);
  // Simulate presence detection flagging the account as shared.
  const doc = gh.content;
  doc.rows[hash].shared = true;
  gh.setExternally(JSON.stringify({ ...doc, sig: "" }));

  await worker.fetch(signedRequest(basilEvent("invoice.paid", end + 30 * DAY, EMAIL, "evt_s2")), e, CTX);
  assert.equal(gh.content.rows[hash].shared, true, "a payment event must not clear the shared flag");
});

test("row floor refuses to publish a mass revocation", () => {
  assert.equal(checkRowFloor(100, 80), null);
  assert.match(checkRowFloor(100, 10), /refusing to publish/);
  assert.equal(checkRowFloor(0, 0), null);
});

// ---------------------------------------------------------------------------
// the Worker
// ---------------------------------------------------------------------------
test("healthz reports state without leaking secrets", async () => {
  installGithub(JSON.stringify({ v: 1, generated_at: 1, rows: {}, seen: [], subs: {}, pis: {} }));
  const resp = await worker.fetch(new Request("https://x/healthz"), env(), CTX);
  assert.equal(resp.status, 200);
  const body = await resp.json();
  assert.equal(body.ok, true);
  assert.equal(body.storage, "single JSON file in the public repo (no database)");
  assert.equal(body.pubkey_matches_expected, true);
  const text = JSON.stringify(body);
  assert.ok(!text.includes(SEED_HEX), "the seed must never be echoed");
  assert.ok(!text.includes("github_pat_fake"));
});

test("a checkout webhook activates the row and publishes one signed file", async () => {
  installGithub(null);
  const e = env();
  const end = Math.floor(Date.now() / 1000) + 30 * DAY;

  const resp = await worker.fetch(signedRequest(basilEvent("checkout.session.completed", end)), e, CTX);
  assert.equal(resp.status, 200);
  const body = await resp.json();
  assert.equal(body.applied, true, JSON.stringify(body));
  assert.equal(body.status, "active");
  assert.equal(body.active, true);
  assert.equal(body.published, true);

  // Exactly one write to GitHub, and it verifies.
  assert.equal(gh.putCalls().length, 1);
  const doc = gh.content;
  assert.equal(doc.v, 1);
  const hash = await rowKey(EMAIL);
  assert.equal(doc.rows[hash].status, "active");
  assert.equal(doc.rows[hash].until, end);
  assert.equal(verifyDocument(doc, PUB), true);
  // The client reads only rows/generated_at/sig; the bookkeeping keys ride along.
  assert.ok(doc.seen.length === 1);
  assert.equal(doc.subs.sub_demo, hash);
});

test("the published file verifies under the client's own edsig.py", async () => {
  installGithub(null);
  await worker.fetch(
    signedRequest(basilEvent("checkout.session.completed", Math.floor(Date.now() / 1000) + 30 * DAY)),
    env(),
    CTX
  );
  const doc = gh.content;
  writeFileSync("/tmp/publisher-simple-interop.json", JSON.stringify({ pubkey_b64: PUB, signed_doc: doc }));

  const script = new URL("./verify-with-edsig.py", import.meta.url).pathname;
  const out = execFileSync("python3", [script, "/tmp/publisher-simple-interop.json"], { encoding: "utf-8" });
  assert.match(out, /^ALL OK/m, `edsig.py rejected the published file:\n${out}`);
});

test("a renewal on a Basil-shaped invoice extends access", async () => {
  installGithub(null);
  const e = env();
  const first = Math.floor(Date.now() / 1000) + 30 * DAY;
  const second = Math.floor(Date.now() / 1000) + 60 * DAY;

  await worker.fetch(signedRequest(basilEvent("checkout.session.completed", first, EMAIL, "evt_a")), e, CTX);
  await worker.fetch(signedRequest(basilEvent("invoice.paid", second, EMAIL, "evt_b")), e, CTX);

  const hash = await rowKey(EMAIL);
  assert.equal(gh.content.rows[hash].until, second, "the renewal must extend the horizon");
});

test("a replayed event is applied once", async () => {
  installGithub(null);
  const e = env();
  const event = basilEvent("checkout.session.completed", Math.floor(Date.now() / 1000) + 30 * DAY, EMAIL, "evt_dup");

  const first = await worker.fetch(signedRequest(event), e, CTX);
  assert.equal((await first.json()).applied, true);
  const writesAfterFirst = gh.putCalls().length;

  const second = await worker.fetch(signedRequest(event), e, CTX);
  const body = await second.json();
  assert.equal(second.status, 200, "200 so Stripe stops retrying");
  assert.equal(body.applied, false);
  assert.equal(body.reason, "already processed");
  assert.equal(gh.putCalls().length, writesAfterFirst, "no second publish for a replay");
});

test("a forged signature is rejected and nothing is written", async () => {
  installGithub(null);
  const body = JSON.stringify(basilEvent("checkout.session.completed", NOW + DAY));
  const ts = Math.floor(Date.now() / 1000);
  const resp = await worker.fetch(
    new Request("https://x/webhooks/stripe", {
      method: "POST",
      body,
      headers: { "stripe-signature": `t=${ts},v1=${"0".repeat(64)}` },
    }),
    env(),
    CTX
  );
  assert.equal(resp.status, 400);
  assert.equal(gh.putCalls().length, 0);
});

test("a missing signing secret is 503, not a 5xx Stripe retries for days", async () => {
  installGithub(null);
  const resp = await worker.fetch(
    signedRequest(basilEvent("checkout.session.completed", NOW + DAY)),
    env({ STRIPE_WEBHOOK_SIGNING_SECRET: "" }),
    CTX
  );
  assert.equal(resp.status, 503);
});

test("a subscription deleted with no email still finds its row via subs", async () => {
  installGithub(null);
  const e = env();
  const end = Math.floor(Date.now() / 1000) + 30 * DAY;
  await worker.fetch(signedRequest(basilEvent("checkout.session.completed", end, EMAIL, "evt_c1")), e, CTX);

  // customer.subscription.deleted often carries only the subscription object.
  const deleted = {
    id: "evt_del",
    type: "customer.subscription.deleted",
    created: Math.floor(Date.now() / 1000) + 5,
    data: { object: { id: "sub_demo", status: "canceled", current_period_end: Math.floor(Date.now() / 1000) } },
  };
  const resp = await worker.fetch(signedRequest(deleted), e, CTX);
  const body = await resp.json();
  assert.equal(body.applied, true, JSON.stringify(body));
  assert.equal(body.status, "canceled");

  const hash = await rowKey(EMAIL);
  assert.equal(gh.content.rows[hash].status, "canceled");
});

test("a refund revokes, and an older replayed checkout cannot resurrect it", async () => {
  installGithub(null);
  const e = env();
  const end = Math.floor(Date.now() / 1000) + 30 * DAY;
  await worker.fetch(signedRequest(basilEvent("checkout.session.completed", end, EMAIL, "evt_r1")), e, CTX);

  const refund = {
    id: "evt_refund",
    type: "charge.refunded",
    created: Math.floor(Date.now() / 1000) + 10,
    data: { object: { customer_email: EMAIL, receipt_email: EMAIL } },
  };
  await worker.fetch(signedRequest(refund), e, CTX);
  const hash = await rowKey(EMAIL);
  assert.equal(gh.content.rows[hash].status, "refunded");

  const replay = basilEvent("checkout.session.completed", end, EMAIL, "evt_replay");
  replay.created = Math.floor(Date.now() / 1000) - 100; // older than the refund
  await worker.fetch(signedRequest(replay), e, CTX);
  assert.equal(gh.content.rows[hash].status, "refunded", "an older event must not un-refund");
});

test("an irrelevant event is acknowledged without writing", async () => {
  installGithub(null);
  const resp = await worker.fetch(
    signedRequest({ ...basilEvent("customer.created", NOW + DAY), type: "customer.created" }),
    env(),
    CTX
  );
  assert.equal((await resp.json()).applied, false);
  assert.equal(gh.putCalls().length, 0);
});

test("a concurrent publish conflicts and is retried, not clobbered", async () => {
  installGithub(JSON.stringify({ v: 1, generated_at: 1, rows: {}, seen: [], subs: {}, pis: {} }));
  const e = env();

  // Make the first write collide: after the Worker reads the file, someone else
  // writes to it, so the Worker's sha is stale and GitHub answers 409.
  const originalPut = gh.fetch;
  let intercepted = false;
  globalThis.fetch = async (url, init) => {
    if (!intercepted && String(init?.method || "GET").toUpperCase() === "PUT") {
      intercepted = true;
      gh.setExternally(
        JSON.stringify({ v: 1, generated_at: 2, rows: {}, seen: [], subs: {}, pis: {} })
      );
    }
    return originalPut(url, init);
  };

  const resp = await worker.fetch(
    signedRequest(basilEvent("checkout.session.completed", Math.floor(Date.now() / 1000) + 30 * DAY, EMAIL, "evt_cas")),
    e,
    CTX
  );
  const body = await resp.json();
  assert.equal(body.applied, true, JSON.stringify(body));
  assert.ok(body.attempt >= 2, `expected a retry after the conflict, attempt=${body.attempt}`);
  assert.equal(gh.putCalls().length >= 2, true);
});

test("/entitlements.json is served signed and verifiable", async () => {
  installGithub(null);
  const e = env();
  await worker.fetch(
    signedRequest(basilEvent("checkout.session.completed", Math.floor(Date.now() / 1000) + 30 * DAY)),
    e,
    CTX
  );
  const resp = await worker.fetch(new Request("https://x/entitlements.json"), e, CTX);
  assert.equal(resp.status, 200);
  const doc = await resp.json();
  assert.equal(verifyDocument(doc, PUB), true);
  assert.deepEqual(Object.keys(doc).sort(), ["cursor", "generated_at", "rows", "sig", "v"]);
});

test("admin endpoints require the token", async () => {
  installGithub(JSON.stringify({ v: 1, generated_at: 1, rows: {}, seen: [], subs: {}, pis: {} }));
  const e = env();
  assert.equal((await worker.fetch(new Request("https://x/admin/state"), e, CTX)).status, 401);
  assert.equal(
    (await worker.fetch(new Request("https://x/admin/state", { headers: { "x-admin-token": "nope" } }), e, CTX)).status,
    401
  );
  assert.equal(
    (await worker.fetch(new Request("https://x/admin/state", { headers: { "x-admin-token": "admin-token" } }), e, CTX))
      .status,
    200
  );
});

test("admin lookup answers why a customer is locked out", async () => {
  installGithub(null);
  const e = env();
  await worker.fetch(
    signedRequest(basilEvent("checkout.session.completed", Math.floor(Date.now() / 1000) + 30 * DAY)),
    e,
    CTX
  );
  const resp = await worker.fetch(
    new Request(`https://x/admin/lookup?email=${encodeURIComponent(EMAIL)}`, {
      headers: { "x-admin-token": "admin-token" },
    }),
    e,
    CTX
  );
  const body = await resp.json();
  assert.equal(body.found, true);
  assert.equal(body.status, "active");
  assert.equal(body.active, true);
  assert.deepEqual(body.known_subscriptions, ["sub_demo"]);
  assert.ok(!JSON.stringify(body).includes(EMAIL), "the plaintext email must not be echoed");
});

test("admin grant replaces builder.py --grant", async () => {
  installGithub(null);
  const e = env();
  const resp = await worker.fetch(
    new Request("https://x/admin/grant", {
      method: "POST",
      headers: { "x-admin-token": "admin-token", "content-type": "application/json" },
      body: JSON.stringify({ email: "grace@example.com", days: 30, reason: "chargeback grace" }),
    }),
    e,
    CTX
  );
  assert.equal(resp.status, 200);
  const body = await resp.json();
  assert.equal(body.status, "grant");
  assert.equal(body.active, true);

  const bad = await worker.fetch(
    new Request("https://x/admin/grant", {
      method: "POST",
      headers: { "x-admin-token": "admin-token", "content-type": "application/json" },
      body: JSON.stringify({ email: "x@example.com", days: 99999, reason: "no" }),
    }),
    e,
    CTX
  );
  assert.equal(bad.status, 400);
});

test("signDocument refuses when the seed does not match the pinned pubkey", () => {
  assert.throws(
    () => signDocument({ v: 1, rows: {} }, SEED_HEX, "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="),
    /does not derive/
  );
});

test("tampering breaks verification", () => {
  const signed = signDocument(buildDocument({ aaa: { status: "active", until: NOW + DAY } }, NOW), SEED_HEX, PUB);
  assert.equal(verifyDocument(signed, PUB), true);
  assert.equal(verifyDocument({ ...signed, generated_at: 1 }, PUB), false);
  assert.equal(verifyDocument({ ...signed, rows: {} }, PUB), false);
  assert.equal(verifyDocument({ ...signed, seen: ["forged"] }, PUB), false);
});

test("unknown routes are 404", async () => {
  installGithub(null);
  for (const path of ["/", "/stripe", "/admin/nope"]) {
    const resp = await worker.fetch(new Request(`https://x${path}`), env(), CTX);
    assert.equal(resp.status, resp.status === 401 ? 401 : 404, path);
  }
});

test("a missing GITHUB_PAT is reported, not a bare 500", async () => {
  installGithub(null);
  const resp = await worker.fetch(
    signedRequest(basilEvent("checkout.session.completed", NOW + DAY)),
    env({ GITHUB_PAT: "" }),
    CTX
  );
  assert.equal(resp.status, 503);
  assert.match((await resp.json()).error, /GITHUB_PAT/);
});
