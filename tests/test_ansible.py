from __future__ import annotations

from importlib import import_module

import jinja2
import pytest

from .testlib import RendererFixture

try:
    import_module("ansible")
except ModuleNotFoundError:
    pytestmark = pytest.mark.skip(reason="ansible is not installed")


def test_ansible_filter(renderer: RendererFixture) -> None:
    assert renderer.eval("[1, [2]] | ansible.builtin.flatten") == [1, 2]


def test_ansible_test(renderer: RendererFixture) -> None:
    assert renderer.eval("[[1], [2]] | select('ansible.builtin.contains', 2)") == [[2]]


def test_ansible_missing(renderer: RendererFixture) -> None:
    with pytest.raises(jinja2.TemplateSyntaxError):
        assert renderer.eval("42 | ansible.foo.missing")
