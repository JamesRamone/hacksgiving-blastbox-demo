"""slugify-lite: minimal, stdlib-only URL slug helper."""

from __future__ import annotations

import re
import unicodedata

__version__ = "0.2.0"

_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str, separator: str = "-", max_length: int | None = None) -> str:
    """Convert arbitrary text into a lowercase ASCII URL slug."""
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    collapsed = _NON_ALNUM_RE.sub(separator, ascii_text).strip(separator)
    if max_length is not None and max_length > 0 and len(collapsed) > max_length:
        collapsed = collapsed[:max_length].rstrip(separator)
    return collapsed
