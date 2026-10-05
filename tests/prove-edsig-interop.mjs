/**
 * PROOF: does the signature this Worker produces verify under the client's own
 * hand-rolled edsig.py?
 *
 * This is the load-bearing question for the whole publisher. If the answer is
 * no, every shipped exe rejects the file and the failure is a total lockout that
 * looks like a server outage. So it is answered in isolation, first, before
 * anything is built on top of it.
 *
 * It exercises the REAL signing path (src/signing.js, tweetnacl) rather than
 * WebCrypto. That choice is deliberate: Cloudflare exposes Ed25519 as
 * `NODE-ED25519` and refuses raw private-key import, while Node calls the same
 * algorithm `Ed25519` — so a WebCrypto implementation needs two code paths and
 * can only ever be tested on one of them. tweetnacl behaves identically in both,
 * which means the tests running in Node are testing the code that runs in the
 * Worker.
 *
 *   node prove-edsig-interop.mjs [seed-hex-or-base64]
 *   python3 tests/verify-with-edsig.py /tmp/interop.json
 *
 * Or both at once:  npm run interop
 */

import { writeFileSync } from "node:fs";

import { buildDocument } from "../worker/publisher-simple/source/src/entitlements.js";
import { canonicalBytes, publicKeyB64, signDocument, verifyDocument } from "../worker/publisher-simple/source/src/signing.js";

const seedArg = process.argv[2] ?? "11".repeat(32);
const seedHex = /^[0-9a-fA-F]{64}$/.test(seedArg.trim())
  ? seedArg.trim().toLowerCase()
  : Buffer.from(seedArg.trim(), "base64").toString("hex");

const pub = publicKeyB64(seedHex);
console.log("seed (hex)       :", seedHex);
console.log("public key (b64) :", pub);
console.log("public key bytes :", Buffer.from(pub, "base64").length);

// A document shaped exactly like the published entitlements.json.
const now = Math.floor(Date.now() / 1000);
const doc = buildDocument(
  {
    "0e2f6a5c8d1b47e9f3a2c6d8015b94e7f2a1c3d6e8b0479f1a2c3d4e5f607182": {
      status: "active",
      plan: "monthly",
      until: now + 30 * 86400,
    },
    "1f3a7b6d9e2c58f0a4b3d7e9126c05f8a3b2d4e7f9c1580a2b3c4d5e6f708193": {
      status: "trial",
      plan: "trial",
      until: now + 2 * 86400,
      shared: true,
    },
  },
  now
);

const signed = signDocument(doc, seedHex, pub);

// Self-check before handing it to Python: if we cannot verify our own output,
// nothing downstream matters.
if (!verifyDocument(signed, pub)) {
  console.error("FATAL: signDocument output does not verify against its own key");
  process.exit(1);
}

const canonical = new TextDecoder().decode(canonicalBytes(signed));
console.log("canonical bytes  :", canonical.length);
console.log("canonical (head) :", canonical.slice(0, 96) + "...");
console.log("signature (b64)  :", signed.sig);

writeFileSync(
  "/tmp/interop.json",
  JSON.stringify({ pubkey_b64: pub, seed_hex: seedHex, signed_doc: signed }, null, 2)
);
console.log("\nwrote /tmp/interop.json");
console.log("now run: python3 tests/verify-with-edsig.py /tmp/interop.json");
