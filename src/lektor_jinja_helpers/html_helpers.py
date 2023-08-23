from __future__ import annotations

import enum
import re
import sys
from typing import Final
from typing import Literal
from typing import Protocol

import bs4
from excerpt_html import excerpt_html as _excerpt_html
from markupsafe import Markup

if sys.version_info >= (3, 11):
    from typing import Never
else:
    from typing import NoReturn as Never


__all__ = ["adjust_heading_levels", "excerpt_html"]


class HasHTML(Protocol):
    @property
    def __html__(self) -> str:
        ...


def _null_normalizer(orig_level: int) -> int:
    return orig_level


class _HeadingLevelNormalizer:
    # Track the original levels of the the headings above the current
    # position in the heading tree.
    orig_levels: list[int]

    def __init__(self) -> None:
        self.orig_levels: list[int] = []

    def __call__(self, orig_level: int) -> int:
        # Look back up the tree to find a the parent of the current
        # heading.  A parent heading is the closest heading in the
        # tree with a lower original level.
        orig_levels = self.orig_levels
        while orig_levels and orig_levels[-1] >= orig_level:
            orig_levels.pop()
        orig_levels.append(orig_level)
        return len(orig_levels)


def adjust_heading_levels(
    html_text: str | HasHTML,
    demote: Literal[0, 1, 2, 3, 4, 5] = 0,
    normalize: bool = True,
) -> Markup:
    """Adjust heading levels in HTML text.

    This is useful, for example, when embedding a ``markup``
    or other HTML-valued field within a larger page structure.

    E.g., if ``this.body`` is a ``markup`` field, the following will ensure
    correct heading structure by ensuring that the headings within the body
    start at ``<h2>``:

        <h1>{{ this.title }}</h1>
        <div class="body">
          {{ this.body | helpers.adjust_heading_levels(demote=1) }}
        </div>

    If ``normalize`` is *true* (the default), heading levels will
    first be normalized so that the heading tree is correct and is
    rooted at ``<h1>``.

    Then each heading is demoted by an amount specified by the
    ``demote`` argument. By default, ``demote`` is zero, so that no
    heading demotion is performed. Passing ``demote=1`` will convert
    ``<h1>`` headings to ``<h2>``, ``<h2>`` to ``<h3>``, and so on.

    Headings are never demoted past ``<h6>``.

    """
    soup = bs4.BeautifulSoup(Markup.escape(html_text), "html5lib")
    # Some parsers add html/body to parse result.  Get rid of that.
    if soup.html:
        soup.html.unwrap()
    while soup.head:
        soup.head.decompose()
    if soup.body:
        soup.body.unwrap()

    normalizer = _null_normalizer
    if normalize:
        normalizer = _HeadingLevelNormalizer()

    for tag in soup.find_all(re.compile(r"(?i)\Ah[1-6]\Z")):
        orig_level = int(tag.name[1:])
        level = normalizer(orig_level) + demote
        tag.name = f"h{min(level, 6):d}"
        if level > 6:
            tag["aria-level"] = f"{level:d}"
        else:
            del tag["aria-level"]

    return Markup(soup.decode())


class _NotSetType(enum.Enum):
    NOT_SET = None


_NOT_SET: Final = _NotSetType.NOT_SET


def excerpt_html(
    html_text: str | HasHTML,
    min_words: int | None | _NotSetType = _NOT_SET,
    cut_mark: str | re.Pattern[str] | None | _NotSetType = _NOT_SET,
    **kwargs: Never,
) -> Markup:
    """A Jinja2 filter to extract leading portion of HTML text.

    This is useful, for example, in order to be able to generate a
    summary of a blog post from the post body.

    - If an explicit *cut-mark* — an HTML comment whose text matches
      ``cut_mark`` — is found, the text will be truncated there.

    - If no explicit cut-mark is found, an attempt will be made to
      find a suitable implicit truncation point. Only points that are
      not within in-line markup are considered. The text will be
      truncated at the first such location found which preserves at
      least ``min_words`` (by default, 50) words of text.

    In either case, the returned excerpt will always be a
    syntactically valid HTML fragment.

    Input passed as plain (“unsafe”) strings will be escaped.

    The return value is always a “safe” ``Markup`` instance.

    """
    vars = locals()
    args = {
        arg: vars[arg] for arg in ("min_words", "cut_mark") if vars[arg] is not _NOT_SET
    }
    markup = Markup.escape(html_text)
    excerpt = _excerpt_html(markup, **args, **kwargs)
    if excerpt is not None:
        return Markup(excerpt)
    return markup
