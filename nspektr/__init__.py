from __future__ import annotations

import contextlib
import functools
import itertools
from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Iterator, TypeVar

from jaraco.context import suppress
from jaraco.functools import apply
from more_itertools import always_iterable
from packaging.markers import Marker
from packaging.requirements import Requirement
from packaging.version import Version

from ._compat import metadata, repair_extras

if TYPE_CHECKING:
    from typing_extensions import Literal, Self

_T = TypeVar("_T")


def resolve(req: Requirement) -> metadata.Distribution:
    """
    Resolve the requirement to its distribution.

    Ignore exception detail for Python 3.9 compatibility.

    >>> resolve(Requirement('pytest<3'))  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    importlib.metadata.PackageNotFoundError: No package metadata was found for pytest<3
    """
    dist = metadata.distribution(req.name)
    if not req.specifier.contains(Version(dist.version), prereleases=True):
        raise metadata.PackageNotFoundError(str(req))
    dist.extras = req.extras  # type: ignore[attr-defined] # Adding extras as if this was an EntryPoint
    return dist


@apply(bool)
@suppress(metadata.PackageNotFoundError)
def is_satisfied(req: Requirement) -> metadata.Distribution:
    return resolve(req)


unsatisfied = functools.partial(itertools.filterfalse, is_satisfied)


class NullMarker:
    @classmethod
    def wrap(cls, req: Requirement) -> Marker | Self:
        return req.marker or cls()

    def evaluate(self, *args: object, **kwargs: object) -> Literal[True]:
        return True


def find_direct_dependencies(
    dist: metadata.Distribution, extras: str | Iterable[str | None] | None = None
) -> itertools.chain[Requirement]:
    """
    Find direct, declared dependencies for dist.
    """
    simple = (
        req
        for req in map(Requirement, always_iterable(dist.requires))
        if NullMarker.wrap(req).evaluate(dict(extra=""))
    )
    extra_deps = (
        req
        for req in map(Requirement, always_iterable(dist.requires))
        for extra in always_iterable(getattr(dist, 'extras', extras))
        if NullMarker.wrap(req).evaluate(dict(extra=extra))
    )
    return itertools.chain(simple, extra_deps)


def traverse(items: Iterator[_T], visit: Callable[[_T], Iterable[_T]]) -> Iterator[_T]:
    """
    Given an iterable of items, traverse the items.

    For each item, visit is called to return any additional items
    to include in the traversal.
    """
    while True:
        try:
            item = next(items)
        except StopIteration:
            return
        yield item
        items = itertools.chain(items, visit(item))


def find_req_dependencies(req: Requirement) -> Iterator[Requirement]:
    with contextlib.suppress(metadata.PackageNotFoundError):
        dist = resolve(req)
        yield from find_direct_dependencies(dist)


def find_dependencies(
    dist: metadata.Distribution, extras: str | Iterable[str | None] | None = None
) -> Iterator[Requirement]:
    """
    Find all reachable dependencies for dist.

    dist is an importlib.metadata.Distribution (or similar).
    TODO: create a suitable protocol for type hint.

    >>> deps = find_dependencies(resolve(Requirement('nspektr')))
    >>> all(isinstance(dep, Requirement) for dep in deps)
    True
    >>> not any('pytest' in str(dep) for dep in deps)
    True
    >>> test_deps = find_dependencies(resolve(Requirement('nspektr[test]')))
    >>> any('pytest' in str(dep) for dep in test_deps)
    True
    """

    def visit(
        req: Requirement, seen: set[Requirement] = set()
    ) -> tuple[()] | Iterator[Requirement]:
        if req in seen:
            return ()
        seen.add(req)
        return find_req_dependencies(req)

    return traverse(find_direct_dependencies(dist, extras), visit)


class Unresolved(Exception):
    def __iter__(self) -> Iterator[Requirement]:
        return iter(self.args[0])


def missing(ep: metadata.EntryPoint) -> itertools.filterfalse[Requirement]:
    """
    Generate the unresolved dependencies (if any) of ep.
    """
    return unsatisfied(find_dependencies(ep.dist, repair_extras(ep.extras)))  # type: ignore[arg-type] # FIXME


def check(ep: metadata.EntryPoint) -> None:
    """
    >>> ep, = metadata.entry_points(group='console_scripts', name='pytest')
    >>> check(ep)
    >>> dist = metadata.distribution('nspektr')

    Since 'docs' extras are not installed, requesting them should fail.

    >>> ep = metadata.EntryPoint(
    ...     group=None, name=None, value='nspektr [doc]')._for(dist)
    >>> check(ep)
    Traceback (most recent call last):
    ...
    nspektr.Unresolved: [...]
    """
    missed = list(missing(ep))
    if missed:
        raise Unresolved(missed)
