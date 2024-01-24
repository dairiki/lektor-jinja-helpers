from __future__ import annotations

from collections import deque
from typing import Iterable
from typing import Iterator

from lektor.assets import Asset
from lektor.db import Page
from lektor.db import Record
from lektor.sourceobj import SourceObject
from lektor.sourceobj import VirtualSourceObject


def lineage(obj: SourceObject, include_self: bool = True) -> Iterator[SourceObject]:
    """Iterate over the lineage of a Lektor source object.

    This Jinja filter expects a Lektor source object (e.g. a DB Record or an Asset)
    as input and returns a generator that yields first (optionally) the input object,
    then the object's parent, and so on up the tree.

    The ``include_self`` parameter controls whether the input object
    is included in the results.

    """
    if not isinstance(obj, (Asset, Record, VirtualSourceObject)):
        msg = (
            "helper.lineage expects a Record, VirtualSourceObject or an Asset,"
            f" not {obj!r}"
        )
        raise TypeError(msg)

    # Note: lineage is not a generator so that TypeError can be raised
    # immediately when the filter is called, rather than when it is
    # first iterated.
    def ancestors() -> Iterator[SourceObject]:
        if include_self:
            yield obj
        ancestor = obj.parent
        while ancestor is not None:
            yield ancestor
            ancestor = ancestor.parent

    return ancestors()


def descendants(
    root: Page,
    include_undiscoverable: bool = False,
    include_hidden: bool = False,
    include_self: bool = True,
    depth_first: bool = False,
) -> Iterator[Page]:
    """Iterate over descendant pages.

    This Jinja filter expects a Lektor Page as input and returns a
    generator which yields first (optionally) the input page, then the
    page's descendants.

    The ``include_self`` parameter controls whether the input page
    is included in the results.

    The ``depth_first`` parameter controls the traversal order.  By
    default, the traversal is breadth-first.

    The ``include_hidden`` and ``include_undiscoverable`` parameters control
    whether hidden and undiscoverable pages are included in the result.
    Note that, since hidden pages are always undiscoverable, to include hidden pages,
    one must set ``include_undiscoverable`` as well as ``include_hidden``.

    """
    if not isinstance(root, Page):
        msg = f"helper.descendants expects a Page, not {root!r}"
        raise TypeError(msg)

    if root.is_hidden and not include_hidden:
        return iter([])
    if root.is_undiscoverable and not include_undiscoverable:
        return iter([])

    def children(page: Page) -> Iterable[Page]:
        return (  # type: ignore[no-any-return]
            page.children.include_hidden(include_hidden).include_undiscoverable(
                include_undiscoverable
            )
        )

    # Note: the oouter descendants() is not a generator so that
    # TypeError can be raised immediately when the filter is called,
    # rather than when it is first iterated.
    def generator() -> Iterator[Page]:
        if include_self:
            yield root
        descendants = deque(children(root))
        while descendants:
            page = descendants.popleft()
            yield page
            if depth_first:
                descendants = deque(children(page)) + descendants
            else:
                descendants.extend(children(page))

    return generator()
