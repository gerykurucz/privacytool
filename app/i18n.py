FALLBACK = "en"
LANGUAGES = [("en", "English", "English")]
STRINGS = {"en": {}}
_current = "en"
_ALL_KEYS = []


def codes():
    return ["en"]


def native_name(code="en"):
    return "English"


def english_name(code="en"):
    return "English"


def publish(code, mapping):
    try:
        STRINGS.setdefault(code, {}).update(dict(mapping))
    except Exception:
        pass


def register_keys(keys):
    global _ALL_KEYS
    try:
        _ALL_KEYS = sorted(set(keys))
    except Exception:
        _ALL_KEYS = []


def coverage(code="en"):
    return 1.0


def is_complete(code="en"):
    return code == "en"


def offered_codes():
    return ["en"]


def in_progress():
    return []


def diagnose():
    return []


def english_only_keys():
    return []


def current():
    return "en"


def set_language(code="en"):
    global _current
    _current = "en"
    return "en"


def L(key, *args):
    try:
        text = STRINGS.get(_current, {}).get(key, STRINGS["en"].get(key, key))
    except Exception:
        text = key
    if args:
        try:
            return text % args
        except (TypeError, ValueError):
            return text
    return text
