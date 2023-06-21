v0.4.0
======

#1: doctest on ``check()`` uses ``pytest`` instead of ``pip`` for
broader compatibility.

v0.3.0
======

``check()`` now raises an ``Unresolved`` exception, an iterable
indicating the unresolved dependencies.

Added ``missing()`` method to generate missing dependencies for
an EntryPoint.

v0.2.0
======

Added backward compatibility for EntryPoint objects as found in
older importlib metadata implementations.

v0.1.0
======

Experimental initial implementation. Supplies ``check`` function
for checking an ep for validity.
