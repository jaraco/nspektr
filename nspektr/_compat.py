from __future__ import annotations

import sys
from collections.abc import Iterable
from re import Match

if sys.version_info >= (3, 10):
    import importlib.metadata as _metadata
else:  # pragma: no cover #jaraco/skeleton#130
    import importlib_metadata as _metadata  # noqa: F401

metadata = _metadata  # Explicit re-export


def repair_extras(extras: list[str] | Iterable[Match[str]]) -> list[str]:
    """
    Repair extras that appear as match objects.

    python/importlib_metadata#369 revealed a flaw in the EntryPoint
    implementation. This function wraps the extras to ensure
    they are proper strings even on older implementations.
    """
    try:
        return list(item.group(0) for item in extras)  # type: ignore[union-attr] # Explicitly repairing this error
    except AttributeError:
        return extras  # type: ignore[return-value] # On a single failure we assume it's all strings
