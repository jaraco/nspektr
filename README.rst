.. image:: https://img.shields.io/pypi/v/nspektr.svg
   :target: https://pypi.org/project/nspektr

.. image:: https://img.shields.io/pypi/pyversions/nspektr.svg

.. image:: https://github.com/jaraco/nspektr/actions/workflows/main.yml/badge.svg
   :target: https://github.com/jaraco/nspektr/actions?query=workflow%3A%22tests%22
   :alt: tests

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

.. image:: https://readthedocs.org/projects/nspektr/badge/?version=latest
   :target: https://nspektr.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/badge/skeleton-2025-informational
   :target: https://blog.jaraco.com/skeleton


nspektr is a distribution package dependency inspector.

It combines functionality from ``importlib.metadata`` and ``packaging``
to provide routines to resolve and validate dependencies for a package
or entry point.

Highlights:

- ``resolve`` takes a requirement and returns a distribution satisfying
  that requirement (disregarding dependencies).
- ``find_dependencies`` takes a metadata.Distribution and generates all
  dependencies transitively as installed in the environment, avoiding
  loops.
- ``missing`` takes an entry point and identifies all unsatisfied
  dependencies for that entry point.
