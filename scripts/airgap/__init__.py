"""Air-gap deploy/update tooling for RECRUIT.

Stdlib-only at runtime (this package is copied onto hosts with no network
access, so nothing beyond the Python standard library can be assumed
installed). Tests may use pytest, but pytest is never required to run the
tools themselves.
"""

from __future__ import annotations
