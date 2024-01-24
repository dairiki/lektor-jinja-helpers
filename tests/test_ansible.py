from __future__ import annotations

from importlib import import_module

import jinja2
import pytest

from .testlib import RendererFixture

from lektor_jinja_helpers.ansible import _FilterKeys

try:
    import_module("ansible")
    no_ansible = False
except ModuleNotFoundError:
    no_ansible = True


requires_ansible = pytest.mark.skipif(no_ansible, reason="ansible is not installed")


@requires_ansible
def test_ansible_filter(renderer: RendererFixture) -> None:
    assert renderer.eval("'a' | ansible.builtin.extract({'a': 42})") == 42


@requires_ansible
def test_ansible_filter_missing(renderer: RendererFixture) -> None:
    with pytest.raises(jinja2.TemplateSyntaxError):
        assert renderer.eval("42 | ansible.foo.missing")


@requires_ansible
def test_ansible_filter_names_fully_qualified(jinja_env: jinja2.Environment) -> None:
    assert "extract" not in jinja_env.filters
    assert "extract" not in list(jinja_env.filters)
    with pytest.raises(KeyError):
        jinja_env.filters["extract"]


@requires_ansible
def test_ansible_test(renderer: RendererFixture) -> None:
    assert renderer.eval(
        "[[1], [2]] | select('ansible.builtin.contains', 2) | list"
    ) == [[2]]


def test_FilterKeys_filters_keys() -> None:
    map = {"a": 1, "B": 2}

    def key_filter(key: object) -> bool:
        return isinstance(key, str) and key.isupper()

    filtered = _FilterKeys(map, key_filter)

    assert filtered.get("a") is None
    assert filtered.get("B") == 2

    with pytest.raises(KeyError):
        filtered["c"] = 3
    filtered["D"] = 4
    assert map["D"] == 4

    with pytest.raises(KeyError):
        del filtered["a"]
    with pytest.raises(KeyError):
        del filtered["b"]
    del filtered["D"]
    assert "D" not in map

    assert "a" not in list(filtered)
    assert "B" in list(filtered)

    assert len(filtered) == 1

    assert "a" not in filtered
    assert "B" in filtered
