from __future__ import annotations

from typing import Any

import jinja2


class RendererFixture:
    def __init__(self, env: jinja2.Environment):
        self.env = env

    def render(self, tmpl: str, *args: Any, **kwargs: Any) -> str:
        template = self.env.from_string(tmpl)
        return template.render(*args, **kwargs)

    def __call__(self, tmpl: str, *args: Any, **kwargs: Any) -> str:
        return self.render(tmpl, *args, **kwargs)

    def eval(self, expr: str, *args: Any, **kwargs: Any) -> Any:
        result: list[Any] = []
        context = dict(*args, **kwargs)
        context["__set_result"] = result.append
        self.render(f"{{{{ __set_result({expr}) }}}}", context)
        return result[0]
