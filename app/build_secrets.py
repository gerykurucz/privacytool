
import base64
import hashlib
import os
import sys




_KEY = b"SnappyAI/build-secrets/v1"


_BLOB = {
    "DISCORD_CLIENT_ID": "mVzqIJpPmEVQ4kbHjPhdEwNvEw==",
    "DISCORD_CLIENT_SEC": "0FqFddIc+AA0hkWXzfkBYEc9aGvR6yLEfHXHZbN2dlA=",
    "ENTITLEMENT_BRANCH": "xACpdg==",
    "ENTITLEMENT_PUBKEY": "4lqKf9of1F8uhwq51I4RV3lsHynUlVzQYDeaQqkkf1LuD5tmkRbUIiOYNc0=",
    "ENTITLEMENT_REPO": "zwytaskP0wUHrV+D1qgYV0o/Ti/Zzx3LeCzMTpt8aWs=",
    "PRESENCE_WEBHOOK": (
        "wB2rY9FAjl8AvgOT17sMCVAxSi3d0QCNeyXLS5F9dmuHWOomkUOTR1TmQseB+V0QAm4U"
        "OpP5EeU1Gf4apn13YPcgsHySK+0nDrASsYyZAGt+FW9kxuBekm8z+Wi6dFNP/xypWfFX"
        "0xcivSKS/vtaQmoIb1vVkR2PXg=="),
    "ROW_PEPPER": "",
    "STRIPE_MONTHLY": "wB2rY9FAjl8Gogney70aTkM7CWHTzEbWaTPdfJtEbH3+De0r5U/gKVCGPcmIpA52em4X",
    "STRIPE_TRIAL": "wB2rY9FAjl8Gogney70aTkM7CWHTzEbWaTPdfM1xVC7HIehnkk3rRlzlKZbXgg52em4W",
    "DISPATCH_PAT": "",
}


_ENV = {
    "ENTITLEMENT_REPO":   "SNAPPYAI_ENT_REPO",
    "ENTITLEMENT_BRANCH": "SNAPPYAI_ENT_BRANCH",
    "ENTITLEMENT_PUBKEY": "SNAPPYAI_ENT_PUBKEY",
    "STRIPE_MONTHLY":     "SNAPPYAI_STRIPE_MONTHLY",
    "STRIPE_TRIAL":       "SNAPPYAI_STRIPE_TRIAL",
    "DISCORD_CLIENT_ID":  "SNAPPYAI_OAUTH_DISCORD_CLIENT_ID",
    "DISCORD_CLIENT_SEC": "SNAPPYAI_OAUTH_DISCORD_CLIENT_SECRET",
    "PRESENCE_WEBHOOK":   "SNAPPYAI_PRESENCE_WEBHOOK",
    "ROW_PEPPER":         "SNAPPYAI_ROW_PEPPER",
    "DISPATCH_PAT":       "SNAPPYAI_DISPATCH_PAT",
}

_ks = hashlib.sha256(_KEY).digest()
_cache = {}


def _decode(raw):
    data = base64.b64decode(raw, validate=True)
    return bytes(c ^ _ks[i % len(_ks)]
                 for i, c in enumerate(data)).decode("utf-8")


def _get(name):
    if name in _cache:
        return _cache[name]
    value = ""
    if not getattr(sys, "frozen", False):
        env = _ENV.get(name)
        if env:
            value = os.environ.get(env, "").strip()
    if not value:
        raw = _BLOB.get(name, "")
        if raw:
            try:
                value = _decode(raw)
            except Exception:
                value = ""
    if value:
        _cache[name] = value
    return value






def entitlement_repo():
    return _get("ENTITLEMENT_REPO").strip().strip("/").strip()


def entitlement_branch():
    return _get("ENTITLEMENT_BRANCH").strip() or "live"


def entitlement_pubkey():
    return _get("ENTITLEMENT_PUBKEY").strip()


def stripe_monthly_link():
    return _get("STRIPE_MONTHLY").strip()


def stripe_trial_link():
    return _get("STRIPE_TRIAL").strip()


def discord_client_id():
    return _get("DISCORD_CLIENT_ID").strip()


def discord_client_secret():
    return _get("DISCORD_CLIENT_SEC").strip()


def presence_webhook():
    return _get("PRESENCE_WEBHOOK").strip()


def row_pepper():
    return _get("ROW_PEPPER").strip()


def dispatch_pat():
    return _get("DISPATCH_PAT").strip()


def is_test_mode():
    links = stripe_monthly_link() + stripe_trial_link()
    return "buy.stripe.com/test_" in links


def describe_readiness():
    fatal = []
    advisory = []
    if not entitlement_pubkey():
        fatal.append("no Ed25519 public key - a subscription can never be "
                     "verified, so nobody could ever get past the gate")
    if not discord_client_id():
        fatal.append("no Discord OAuth client id - sign-in is impossible")
    if not entitlement_repo():
        fatal.append("no entitlement repo - there is nowhere to fetch the "
                     "signed subscription file from")
    if is_test_mode():
        advisory.append("the Stripe payment links are still in TEST mode - "
                        "checkout will complete, no money will move, and no "
                        "subscription will ever activate")
    if not row_pepper():
        advisory.append("no row-hash pepper - entitlement rows are keyed by "
                        "unsalted sha256(e-mail) in a PUBLIC file")
    if not presence_webhook():
        advisory.append("no presence webhook - account-sharing detection "
                        "is off")
    return fatal, advisory


def is_shippable():
    fatal, advisory = describe_readiness()
    return not fatal and not advisory




SENSITIVE_KEYS = frozenset((
    "entitlement_repo", "entitlement_branch", "entitlement_pubkey",
    "stripe_monthly_link", "stripe_trial_link",
    "discord_client_id", "discord_client_secret",
    "presence_webhook", "dispatch_pat", "row_pepper",
))
