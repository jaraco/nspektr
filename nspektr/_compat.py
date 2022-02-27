if False:
    # bugfix from 4.11.2 is required
    import importlib.metadata as metadata
else:
    import importlib_metadata as metadata  # type: ignore # noqa: F401
