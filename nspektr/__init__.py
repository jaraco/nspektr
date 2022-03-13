import itertools
import functools
import contextlib

from packaging.requirements import Requirement
from packaging.version import Version
from more_itertools import always_iterable
from jaraco.context import suppress
from jaraco.functools import apply

from ._compat import metadata


def resolve(req: Requirement):
    """
    >>> resolve(Requirement('pytest<3'))
    Traceback (most recent call last):
    ...
    importlib_metadata.PackageNotFoundError: No package metadata was found for pytest<3
    """
    dist = metadata.distribution(req.name)
    if not req.specifier.contains(Version(dist.version), prereleases=True):
        raise metadata.PackageNotFoundError(str(req))
    dist.extras = req.extras  # type: ignore
    return dist


@apply(bool)
@suppress(metadata.PackageNotFoundError)
def is_satisfied(req: Requirement):
    return resolve(req)


unsatisfied = functools.partial(itertools.filterfalse, is_satisfied)


class NullMarker:
    @classmethod
    def wrap(cls, req: Requirement):
        return req.marker or cls()

    def evaluate(self, *args, **kwargs):
        return True


def find_direct_dependencies(dist, extras=None):
    """
    Find direct, declared dependencies for dist.
    """
    simple = (
        req
        for req in map(Requirement, always_iterable(dist.requires))
        if NullMarker.wrap(req).evaluate(dict(extra=None))
    )
    extra_deps = (
        req
        for req in map(Requirement, always_iterable(dist.requires))
        for extra in always_iterable(getattr(dist, 'extras', extras))
        if NullMarker.wrap(req).evaluate(dict(extra=extra))
    )
    return itertools.chain(simple, extra_deps)


def traverse(items):
    """
    Given an iterable of items, traverse the items.

    For each item yielded, the consumer may send back additional
    items to include in the traversal.
    """
    while True:
        try:
            item = next(items)
        except StopIteration:
            return
        additional = yield item
        items = itertools.chain(items, additional or ())


def find_req_dependencies(req):
    with contextlib.suppress(metadata.PackageNotFoundError):
        dist = resolve(req)
        yield from find_direct_dependencies(dist)


def find_dependencies(dist, extras=None):
    """
    Find all reachable dependencies for dist.

    dist is an importlib.metadata.Distribution (or similar).
    TODO: create a suitable protocol for type hint.

    >>> deps = find_dependencies(resolve(Requirement('nspektr')))
    >>> all(isinstance(dep, Requirement) for dep in deps)
    True
    >>> not any('pytest' in str(dep) for dep in deps)
    True
    >>> test_deps = find_dependencies(resolve(Requirement('nspektr[testing]')))
    >>> any('pytest' in str(dep) for dep in test_deps)
    True
    """
    traversal = traverse(find_direct_dependencies(dist, extras))
    with contextlib.suppress(StopIteration):
        req = next(traversal)
        seen = set()
        while True:
            if str(req) in seen:
                req = traversal.send(None)
                continue
            seen.add(str(req))
            yield req
            req = traversal.send(find_req_dependencies(req))


def check(ep):
    """
    >>> ep, = metadata.entry_points(group='console_scripts', name='pip')
    >>> check(ep)
    >>> dist = metadata.distribution('nspektr')

    Since 'docs' extras are not installed, requesting them should fail.

    >>> ep = metadata.EntryPoint(
    ...     group=None, name=None, value='nspektr [docs]')._for(dist)
    >>> check(ep)
    Traceback (most recent call last):
    ...
    ValueError: ('Unable to resolve all dependencies',...
    """
    missing = list(unsatisfied(find_dependencies(ep.dist, ep.extras)))
    if missing:
        raise ValueError("Unable to resolve all dependencies", missing)
