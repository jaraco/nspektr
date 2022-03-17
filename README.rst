.. image:: https://img.shields.io/pypi/v/nspektr.svg
   :target: `PyPI link`_

.. image:: https://img.shields.io/pypi/pyversions/nspektr.svg
   :target: `PyPI link`_

.. _PyPI link: https://pypi.org/project/nspektr

.. image:: https://github.com/jaraco/nspektr/workflows/tests/badge.svg
   :target: https://github.com/jaraco/nspektr/actions?query=workflow%3A%22tests%22
   :alt: tests

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: Black

.. .. image:: https://readthedocs.org/projects/skeleton/badge/?version=latest
..    :target: https://skeleton.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/badge/skeleton-2022-informational
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
