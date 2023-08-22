from .testlib import RendererFixture


def test_import_module(renderer: RendererFixture) -> None:
    r = renderer("{{ helpers.import_module('datetime').date(2023, 1, 2).isoformat() }}")
    assert r == "2023-01-02"


def test_call_filter(renderer: RendererFixture) -> None:
    assert renderer.eval(
        "['a', 'b'] | map('helpers.call', str.center, 5, '-') | list", str=str
    ) == ["--a--", "--b--"]


def test_call_test(renderer: RendererFixture) -> None:
    assert renderer.eval(
        "['a', 'B'] | select('helpers.call', str.isupper) | list", str=str
    ) == ["B"]
