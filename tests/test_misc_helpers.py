from __future__ import annotations

from collections import abc
from typing import Any
from typing import Iterable

import pytest

from .testlib import RendererFixture
from lektor_jinja_helpers.misc_helpers import flatten


def test_call_filter(renderer: RendererFixture) -> None:
    assert renderer.eval(
        "['a', 'b'] | map('helpers.call', str.center, 5, '-') | list", str=str
    ) == ["--a--", "--b--"]


def test_call_test(renderer: RendererFixture) -> None:
    assert renderer.eval(
        "['a', 'B'] | select('helpers.call', str.isupper) | list", str=str
    ) == ["B"]


@pytest.mark.parametrize(
    "iterable, depth, expected",
    [
        ([1, [2, [3, 4]], 5], None, [1, 2, 3, 4, 5]),
        ([1, [2, [3, 4]], 5], 1, [1, 2, [3, 4], 5]),
        (
            ["str", {"a": "mapping"}, [b"bytes"]],
            None,
            ["str", {"a": "mapping"}, b"bytes"],
        ),
        (iter([1, [2]]), None, [1, 2]),
    ],
)
def test_flatten(
    iterable: Iterable[Any], depth: int | None, expected: list[Any]
) -> None:
    result = flatten(iterable, depth=depth)
    assert isinstance(result, abc.Iterator)
    assert list(result) == expected
