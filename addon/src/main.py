import os
import sys
import traceback

from snappy import SnappyAI


def _base_dir():
    """Directory for config/crash logs: next to the exe when frozen,
    otherwise the project root (parent of src/)."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


def main():
    try:
        # Line-buffer stdout/stderr so logs appear live when redirected
        # to a file (block buffering would hide them until exit/kill).
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)
    except Exception:
        pass
    try:
        SnappyAI().run()
    except KeyboardInterrupt:
        print('\nInterrupted, exiting')
        return 0
    except SystemExit:
        raise
    except Exception:
        text = traceback.format_exc()
        print(text)
        try:
            with open(os.path.join(_base_dir(), 'crash.log'), 'a', encoding='utf-8') as f:
                f.write(text + '\n')
            print('Crash details written to crash.log')
        except OSError:
            pass
        if getattr(sys, 'frozen', False):
            # Keep a double-clicked exe window open so the error stays visible
            try:
                input('Fatal error - press Enter to exit...')
            except EOFError:
                pass
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
