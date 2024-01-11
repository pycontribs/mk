from __future__ import annotations

import re


def strip_ansi_escape(text: str | bytes) -> str:
    """Remove all ANSI escapes from string or bytes.

    If bytes is passed instead of string, it will be converted to string
    using UTF-8.
    """
    if isinstance(text, bytes):
        text = text.decode("utf-8")

    return re.sub(r"\x1b[^m]*m", "", text)
