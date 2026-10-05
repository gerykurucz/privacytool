"""Core plumbing: application identity and the logging bus.

The shipping GUI is built --noconsole, so `print` alone would make
every diagnostic line invisible in the field - which is exactly when
diagnostics matter. log() therefore fans out to three places:

  * stdout, when there is one (console build, dev run)
  * a ring buffer, holding the most recent lines in memory
  * an optional capped log file, attached once at start-up

Every sink is best-effort: logging must never be able to break the
product it is describing.
"""

import collections
import os
import threading
import time

APP_NAME = "Snappy AI"
APP_VERSION = "8.49"
IS_WINDOWS = (os.name == "nt")
print_lock = threading.Lock()

RING_LIMIT = 400                  # lines kept in memory
FILE_LIMIT = 512 * 1024           # log file cap: keep the tail

_sinks = []
_ring = collections.deque(maxlen=RING_LIMIT)
_log_path = None
_sinks_wired = False


def log(text):
    """Print one timestamped status line and feed every registered sink."""
    global _sinks_wired
    if not _sinks_wired:
        # Lazy, once, and set BEFORE wiring so a module that logs during its
        # own import cannot re-enter. Wiring lives here rather than in
        # attach_log_file() because that function returns early when the log
        # folder is not writable - and a machine that cannot write a log is
        # exactly the machine whose in-memory diagnostics still matter.
        _sinks_wired = True
        _wire_module_sinks()
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), text)
    with print_lock:
        _ring.append(line)
        try:
            print(line, flush=True)
        except Exception:
            pass                  # --noconsole: there is no stdout
        for sink in list(_sinks):
            try:
                sink(line)
            except Exception:
                pass


def _wire_module_sinks():
    """Push log() into modules that must stay dependency-free leaves.

    vision.py cannot import core (that would make the analysis engine
    depend on the app-identity module and stop it being a pure leaf), but
    it does have one degradation worth reporting - a colour gate that ran
    out of scan budget and therefore failed closed. Injecting the sink
    keeps the dependency arrow pointing the right way."""
    try:
        import vision
        vision.set_log_sink(log)
    except Exception:
        pass


def add_log_sink(fn):
    """Register fn(line) as an extra log destination; returns fn."""
    if callable(fn) and fn not in _sinks:
        _sinks.append(fn)
    return fn


def recent_lines(limit=60):
    """The last `limit` logged lines, oldest first."""
    try:
        limit = max(0, int(limit))
    except (TypeError, ValueError):
        limit = 60
    return list(_ring)[-limit:]


def log_path():
    """Path of the attached log file, or None."""
    return _log_path


def _cap_file(path):
    """Trim a log left behind by an earlier run down to its tail."""
    try:
        size = os.path.getsize(path)
    except OSError:
        return
    if size <= FILE_LIMIT:
        return
    try:
        with open(path, "rb") as fh:
            fh.seek(size - FILE_LIMIT // 2)
            tail = fh.read()
        tail = tail.split(b"\n", 1)[-1]        # drop the partial line
        with open(path, "wb") as fh:
            fh.write(tail)
    except OSError:
        pass


def attach_log_file(path):
    """Append every log line to `path` (created, tail-capped on open).

    Returns the path in use, or None when it could not be opened - the
    app carries on either way. Called once from main()."""
    global _log_path
    try:
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        _cap_file(path)
        handle = open(path, "a", encoding="utf-8", buffering=1)
    except OSError:
        _log_path = None
        return None
    _log_path = path

    def _file_sink(line):
        try:
            handle.write(line + "\n")
        except Exception:
            pass

    add_log_sink(_file_sink)
    log("%s %s log started (pid %d) -> %s"
        % (APP_NAME, APP_VERSION, os.getpid(), path))
    return path
