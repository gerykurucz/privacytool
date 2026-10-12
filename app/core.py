
import collections
import os
import threading
import time

APP_NAME = "Snappy AI"
APP_VERSION = "8.67"
IS_WINDOWS = (os.name == "nt")
print_lock = threading.Lock()

RING_LIMIT = 400
FILE_LIMIT = 512 * 1024

_sinks = []
_ring = collections.deque(maxlen=RING_LIMIT)
_log_path = None
_sinks_wired = False


def log(text):
    global _sinks_wired
    if not _sinks_wired:





        _sinks_wired = True
        _wire_module_sinks()
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), text)
    with print_lock:
        _ring.append(line)
        try:
            print(line, flush=True)
        except Exception:
            pass
        for sink in list(_sinks):
            try:
                sink(line)
            except Exception:
                pass


def _wire_module_sinks():
    try:
        import vision
        vision.set_log_sink(log)
    except Exception:
        pass


def add_log_sink(fn):
    if callable(fn) and fn not in _sinks:
        with print_lock:
            if fn not in _sinks:
                _sinks.append(fn)
    return fn


def recent_lines(limit=60):
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 60
    if limit <= 0:
        return []
    return list(_ring)[-limit:]


def log_path():
    return _log_path


def _cap_file(path):
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
        tail = tail.split(b"\n", 1)[-1]
        with open(path, "wb") as fh:
            fh.write(tail)
    except OSError:
        pass


import atexit as _atexit

_file_handle = None


def attach_log_file(path):
    global _log_path, _file_handle
    if _log_path is not None:
        return _log_path
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
    _file_handle = handle
    try:
        _atexit.register(handle.close)
    except Exception:
        pass

    def _file_sink(line):
        try:
            handle.write(line + "\n")
        except Exception:
            pass

    add_log_sink(_file_sink)
    log("%s %s log started (pid %d) -> %s"
        % (APP_NAME, APP_VERSION, os.getpid(), path))
    return path
