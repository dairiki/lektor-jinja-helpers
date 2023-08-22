import pytest
from markupsafe import Markup

from .testlib import RendererFixture
from lektor_jinja_helpers.html_helpers import _HeadingLevelNormalizer


def test_excerpt_html_escapes_str(renderer: RendererFixture) -> None:
    assert renderer('{{ "<" | helpers.excerpt_html }}') == "&lt;"


def test_excerpt_html_escapes_excerpt(renderer: RendererFixture) -> None:
    excerpt = renderer(
        "{{ str | helpers.excerpt_html }}",
        str="<br>" + Markup("<!-- more --><p>extra</p>"),
    )
    assert excerpt == "&lt;br&gt;"


def test_excerpt_html_cut_mark(renderer: RendererFixture) -> None:
    excerpt = renderer(
        "{{ str | helpers.excerpt_html(cut_mark=' custom ') }}",
        str=Markup("<p>first</p><!-- custom --><p>extra</p>"),
    )
    assert excerpt == "<p>first</p>"


def test_excerpt_html_min_words(renderer: RendererFixture) -> None:
    excerpt = renderer(
        "{{ str | helpers.excerpt_html(min_words=1) }}",
        str=Markup("<p>first</p><p>extra</p>"),
    )
    assert excerpt == "<p>first</p>"


def test_excerpt_html_no_excerpt(renderer: RendererFixture) -> None:
    excerpt = renderer(
        "{{ str | helpers.excerpt_html }}",
        str=Markup("<p>first</p><!-- custom --><p>extra</p>"),
    )
    assert excerpt == "<p>first</p><!-- custom --><p>extra</p>"


@pytest.mark.parametrize(
    "levels, normalized_levels",
    [
        ([1, 2, 3, 3, 2, 4, 4], [1, 2, 3, 3, 2, 3, 3]),
        ([2, 4, 3, 1, 2], [1, 2, 2, 1, 2]),
        ([2, 3, 4, 1, 2], [1, 2, 3, 1, 2]),
    ],
)
def test_HeadingLevelNormalizer(
    levels: list[int], normalized_levels: list[int]
) -> None:
    normalizer = _HeadingLevelNormalizer()
    assert [normalizer(lvl) for lvl in levels] == normalized_levels


def test_adjust_heading_levels(renderer: RendererFixture) -> None:
    excerpt = renderer(
        "{{ str | helpers.adjust_heading_levels(demote=1) }}",
        str=Markup("<h1>first</h1><h3>second</h3>"),
    )
    assert excerpt == "<h2>first</h2><h3>second</h3>"


def test_adjust_heading_levels_no_normalize(renderer: RendererFixture) -> None:
    excerpt = renderer(
        "{{ str | helpers.adjust_heading_levels(demote=1, normalize=false) }}",
        str=Markup("<h1>first</h1><h3>second</h3>"),
    )
    assert excerpt == "<h2>first</h2><h4>second</h4>"


def test_adjust_heading_levels_deep(renderer: RendererFixture) -> None:
    excerpt = renderer(
        "{{ str | helpers.adjust_heading_levels(demote=5) }}",
        str=Markup("<h1>first</h1><h2>second</h2>"),
    )
    assert excerpt == '<h6>first</h6><h6 aria-level="7">second</h6>'
