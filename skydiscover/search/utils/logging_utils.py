"""Logging utilities for the search subsystem.

Provides a compact console formatter, a noise-reducing filter, and a
one-call helper to wire up both file and console logging for a
discovery run.
"""

import logging
import os
import sys
import time

_QUIET = {"route", "server"}


def _force_utf8(stream):
    """Reconfigure a text stream to UTF-8 so Unicode log messages (e.g. arrows)
    don't raise UnicodeEncodeError on Windows, where consoles and redirected
    pipes default to cp1252. No-op if the stream can't be reconfigured."""
    try:
        stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    except (AttributeError, ValueError):
        pass


class _ConsoleFormatter(logging.Formatter):
    """Compact single-line formatter: ``HH:MM:SS [module] message``."""

    def format(self, record):
        ts = self.formatTime(record, "%H:%M:%S")
        name = (
            record.name[len("skydiscover.") :]
            if record.name.startswith("skydiscover.")
            else record.name
        )
        parts = name.split(".")
        short = f"search.{parts[1]}" if parts[0] == "search" and len(parts) >= 3 else parts[-1]
        fmt = (
            f"{ts} {record.levelname} [{short}] "
            if record.levelno >= logging.WARNING
            else f"{ts} [{short}] "
        )
        return fmt + record.getMessage()


class _ConsoleFilter(logging.Filter):
    """Only pass skydiscover messages, suppressing noisy modules below WARNING."""

    def filter(self, record):
        if record.levelno >= logging.WARNING:
            return True
        if not record.name.startswith("skydiscover") or record.name.split(".")[-1] in _QUIET:
            return False
        return True


def setup_search_logging(log_level: str, log_dir: str, name: str) -> None:
    """Configure root logger with a timestamped file handler and a console handler."""
    os.makedirs(log_dir, exist_ok=True)
    root = logging.getLogger()
    root.setLevel(getattr(logging, log_level))

    log_file = os.path.join(log_dir, f"{name}_{time.strftime('%Y%m%d_%H%M%S')}.log")
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    root.addHandler(fh)

    # Console + print() summaries go to stdout/stderr, which are cp1252 on Windows.
    _force_utf8(sys.stdout)
    _force_utf8(sys.stderr)

    if not any(
        isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
        for h in root.handlers
    ):
        ch = logging.StreamHandler()
        ch.setFormatter(_ConsoleFormatter())
        ch.addFilter(_ConsoleFilter())
        root.addHandler(ch)

    logging.getLogger(__name__).info(f"Logging to {log_file}")
