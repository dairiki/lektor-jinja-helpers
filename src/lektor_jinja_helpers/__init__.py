from __future__ import annotations

import importlib
from types import SimpleNamespace
from typing import Any
from typing import Callable
from typing import Concatenate
from typing import ParamSpec
from typing import TypeVar

from lektor.pluginsystem import Plugin

from . import html

_T = TypeVar("_T")
_U = TypeVar("_U")
_P = ParamSpec("_P")


def do_call(
    value: _T,
    function: Callable[Concatenate[_T, _P], _U],
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> _U:
    """Convert a jinja global function to a filter.

    This filter can be used to apply a global function as a
    filter. This can be useful when using the ``map`` filter.

    E.g.

        {% set date = import_module("datetime").date -%}
        {% set dates = ["2023-01-02", "2021-04-01"] -%}
        Min year: {{ (dates | map("helpers.call", date.fromisoformat) | min).year }}

    """
    return function(value, *args, **kwargs)


FILTERS = {
    "adjust_heading_levels": html.adjust_heading_levels,
    "excerpt_html": html.excerpt_html,
    "call": do_call,
}
TESTS = {
    "call": do_call,
}
GLOBALS = {
    "import_module": importlib.import_module,
}


class JinjaHelpersPlugin(Plugin):  # type: ignore[misc]
    name = "jinja-helpers"
    description = "A collection of Jinja2 filters and globals for Lektor"

    def on_setup_env(self, **extra: Any) -> None:
        jinja_env = self.env.jinja_env
        jinja_env.filters.update({f"helpers.{name}": f for name, f in FILTERS.items()})
        jinja_env.tests.update({f"helpers.{name}": f for name, f in TESTS.items()})

        jinja_env.globals["helpers"] = helpers = SimpleNamespace()
        for name, f in GLOBALS.items():
            setattr(helpers, name, f)
