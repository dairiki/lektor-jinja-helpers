from __future__ import annotations

import pytest
from lektor.db import Pad

from .testlib import RendererFixture

from lektor_jinja_helpers.db_helpers import descendants
from lektor_jinja_helpers.db_helpers import lineage


@pytest.mark.parametrize(
    "path, kwargs, expected",
    [
        ("/child-1/child-1a", {}, ["/child-1/child-1a", "/child-1", "/"]),
        ("/child-1", {"include_self": False}, ["/"]),
        ("/", {"include_self": True}, ["/"]),
        ("/", {}, ["/"]),
        ("/", {"include_self": False}, []),
    ],
)
def test_lineage(
    lektor_pad: Pad, path: str, kwargs: dict[str, bool], expected: list[str]
) -> None:
    assert [
        ancest.path for ancest in lineage(lektor_pad.get(path), **kwargs)
    ] == expected


def test_lineage_raises_type_error() -> None:
    with pytest.raises(TypeError):
        lineage(42)


@pytest.mark.parametrize(
    "root, kwargs, expected",
    [
        (
            "/",
            {},
            ["/", "/child-1", "/child-2", "/child-1/child-1a", "/child-1/child-1b"],
        ),
        (
            "/",
            {"include_self": False},
            ["/child-1", "/child-2", "/child-1/child-1a", "/child-1/child-1b"],
        ),
        (
            "/",
            {"depth_first": True},
            ["/", "/child-1", "/child-1/child-1a", "/child-1/child-1b", "/child-2"],
        ),
        (
            "/",
            {"include_self": False, "include_undiscoverable": True},
            [
                "/child-1",
                "/child-2",
                "/child-undiscoverable",
                "/child-1/child-1a",
                "/child-1/child-1b",
            ],
        ),
        (
            "/",
            {
                "include_self": False,
                "include_hidden": True,
                "include_undiscoverable": True,
            },
            [
                "/child-1",
                "/child-2",
                "/child-hidden",
                "/child-undiscoverable",
                "/child-1/child-1a",
                "/child-1/child-1b",
            ],
        ),
        (
            "/child-hidden",
            {
                "include_hidden": True,
                "include_undiscoverable": True,
            },
            [
                "/child-hidden",
            ],
        ),
        (
            "/child-hidden",
            {"include_undiscoverable": True},
            [],
        ),
        (
            "/child-undiscoverable",
            {
                "include_undiscoverable": True,
            },
            [
                "/child-undiscoverable",
            ],
        ),
        (
            "/child-undiscoverable",
            {},
            [],
        ),
    ],
)
def test_descendants(
    lektor_pad: Pad, root: str, kwargs: dict[str, bool], expected: list[str]
) -> None:
    assert [
        desc.path for desc in descendants(lektor_pad.get(root), **kwargs)
    ] == expected


def test_descendants_raises_type_error() -> None:
    with pytest.raises(TypeError):
        descendants({})


def test_integration(renderer: RendererFixture, lektor_pad: Pad) -> None:
    result = renderer(
        "{{ this | helpers.lineage | map(attribute='path') | join(':') }}",
        this=lektor_pad.get("/child-1/child-1b"),
    )
    assert result == "/child-1/child-1b:/child-1:/"
