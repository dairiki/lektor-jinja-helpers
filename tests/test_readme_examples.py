"""Manually constructed tests of examples in the README.md
"""
from __future__ import annotations

import re
from collections.abc import Iterator

from lektor.db import Pad

from .testlib import RendererFixture


def test_descendants_all_images(renderer: RendererFixture, lektor_pad: Pad) -> None:
    images = renderer.eval(
        'site.root | helpers.descendants | map(attribute="attachments.images")'
        "| helpers.flatten",
        site=lektor_pad,
    )
    assert [image["_id"] for image in images] == ["image-1a1.png"]


def test_flatten(renderer: RendererFixture) -> None:
    result = renderer.eval('[["foo", "bar"], ["baz"]] | helpers.flatten')
    assert isinstance(result, Iterator)
    assert list(result) == ["foo", "bar", "baz"]


def test_call_filter(renderer: RendererFixture) -> None:
    assert renderer(
        '{% for r in range(3) | map("helpers.call", range, 4) -%}\n'
        '  {{ r | join(",") }}\n'
        "{% endfor -%}\n"
    ) == "\n".join(
        [
            "0,1,2,3",
            "1,2,3",
            "2,3",
            "",
        ]
    )


def test_call_test(renderer: RendererFixture) -> None:
    result = renderer(
        '{% set isupper = "".__class__.isupper -%}'
        '{{ ["lower", "UPPER"] | select("helpers.call", isupper) | join(",") }}'
    )
    assert result == "UPPER"


def test_import_module(renderer: RendererFixture) -> None:
    now = renderer(
        '{% set date = helpers.import_module("datetime").date -%}'
        "{{ date.today().isoformat() }}"
    )
    assert re.match(r"\d{4}-\d{2}-\d{2}\Z", now)
