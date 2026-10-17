import contextlib


def repair_extras(extras):
    """
    Repair extras that appear as match objects.

    python/importlib_metadata#369 revealed a flaw in the EntryPoint
    implementation. This function wraps the extras to ensure
    they are proper strings even on older implementations.
    """
    with contextlib.suppress(AttributeError):
        return [item.group(0) for item in extras]
    return extras
