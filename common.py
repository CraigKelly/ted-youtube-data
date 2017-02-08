"""Some common helper functions."""

import sys
import inspect


def _flush():
    sys.stderr.flush()
    sys.stdout.flush()


def log(msg, *args):
    """Log to stderr with optional formatting."""
    if args:
        msg = msg % args
    pre = inspect.getfile(sys._getframe(1)) + ": "
    sys.stderr.write(pre + msg + "\n")
    _flush()
