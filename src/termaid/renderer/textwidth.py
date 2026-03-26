"""Unicode-aware text width utilities for terminal rendering.

CJK (Chinese, Japanese, Korean) and other full-width characters occupy
2 terminal columns, while most Latin/ASCII characters occupy 1.
This module provides functions to compute display width correctly,
replacing naive ``len()`` calls throughout the rendering pipeline.

Uses only the standard library (``unicodedata``), keeping termaid's
zero-runtime-dependency guarantee.
"""
from __future__ import annotations

import unicodedata


def char_width(ch: str) -> int:
    """Return the display width of a single character in terminal columns.

    Full-width (F) and wide (W) characters return 2; all others return 1.
    """
    eaw = unicodedata.east_asian_width(ch)
    if eaw in ("W", "F"):
        return 2
    return 1


def display_width(text: str) -> int:
    """Return the total display width of *text* in terminal columns."""
    return sum(char_width(ch) for ch in text)


def display_rjust(text: str, width: int) -> str:
    """Right-justify *text* to *width* display columns."""
    pad = width - display_width(text)
    return " " * max(0, pad) + text


def display_ljust(text: str, width: int) -> str:
    """Left-justify *text* to *width* display columns."""
    pad = width - display_width(text)
    return text + " " * max(0, pad)
