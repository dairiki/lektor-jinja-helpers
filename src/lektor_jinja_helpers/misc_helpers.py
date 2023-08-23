from __future__ import annotations

import sys
from collections import abc
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Iterator
from typing import TypeVar


if sys.version_info >= (3, 10):
    from typing import Concatenate
    from typing import ParamSpec
else:
    from typing_extensions import Concatenate
    from typing_extensions import ParamSpec


__all__ = ["call", "flatten"]


_T = TypeVar("_T")
_U = TypeVar("_U")
_P = ParamSpec("_P")


def call(
    value: _T,
    function: Callable[Concatenate[_T, _P], _U],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> _U:
    """Convert a jinja global function to a filter.

    This filter can be used to apply a global function as a
    filter. This can be useful when using the ``map`` filter.

    E.g.

        {% set date = import_module("datetime").date -%}
        {% set dates = ["2023-01-02", "2021-04-01"] -%}
        Min year: {{ (dates | map("helpers.call", date.fromisoformat) | min).year }}

    """
    return function(value, *args, **kwargs)


def flatten(
    iterable: Iterable[Any],
    depth: int | None = None,
) -> Iterator[Any]:
    """Flatten a nested structure of iterables.

    This filters expects an iterable as input.

    As an example,

        [["foo", "bar"], ["baz"]] | helpers.flatten

    will return a generator that will yield ``"foo"``, ``"bar"``, ``"baz"``.

    The ``depth`` parameter (if not ``None``) limits the maximum depth of
    flattening performed.  If depth is less than or equal to zero, no flattening
    is performed.

    For the sake of flattening, strings and ``Mapping``s are not
    considered to be “iterables”.

    """
    stack = [iter(iterable)]

    def generator() -> Iterator[Any]:
        while stack:
            try:
                obj = next(stack[-1])
            except StopIteration:
                stack.pop()
                continue

            if depth is not None and len(stack) > depth:
                yield obj
            elif isinstance(obj, (str, abc.Mapping)):
                yield obj
            elif isinstance(obj, abc.ByteString):  # type: ignore[arg-type] # mypy bug?
                yield obj
            else:
                try:
                    stack.append(iter(obj))
                except TypeError:
                    yield obj  # not iterable

    return generator()
