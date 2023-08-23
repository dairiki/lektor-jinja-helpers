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
    assert renderer.eval("'a' | ansible.builtin.extract({'a': 42})") == 42


def test_ansible_filter_missing(renderer: RendererFixture) -> None:
    with pytest.raises(jinja2.TemplateSyntaxError):
        assert renderer.eval("42 | ansible.foo.missing")


def test_ansible_filter_names_fully_qualified(jinja_env: jinja2.Environment) -> None:
    assert "extract" not in jinja_env.filters
    with pytest.raises(KeyError):
        jinja_env.filters["extract"]


def test_ansible_test(renderer: RendererFixture) -> None:
    assert renderer.eval(
        "[[1], [2]] | select('ansible.builtin.contains', 2) | list"
    ) == [[2]]
