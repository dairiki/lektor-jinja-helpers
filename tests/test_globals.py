from .testlib import RendererFixture


def test_import_module(renderer: RendererFixture) -> None:
    r = renderer("{{ helpers.import_module('datetime').date(2023, 1, 2).isoformat() }}")
    assert r == "2023-01-02"
