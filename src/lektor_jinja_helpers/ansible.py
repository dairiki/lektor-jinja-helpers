from __future__ import annotations

from collections import ChainMap
from dataclasses import dataclass
from typing import Callable
from typing import Iterator
from typing import MutableMapping
from typing import TypeVar

import jinja2

try:
    import ansible.plugins.loader
    from ansible.template import JinjaPluginIntercept
except ModuleNotFoundError:
    ansible = None

_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


def import_ansible_filters_and_tests(env: jinja2.Environment) -> None:
    """Monkeypatch Jinja environment to make Ansible filters and tests availabled."""
    if ansible is None:
        return  # ansible is not installed

    assert isinstance(env.filters, dict)
    assert isinstance(env.tests, dict)

    _init_ansible()

    # Ansible normally monkey-patches a JinjaPluginIntercept instance
    # directly into jinja's env.filters and env.tests.
    #
    # We can't use JinjaPluginIntercept directly for two reasons:
    #
    # 1. JinjaPluginIntercept tries to load any dotted name via
    #    Ansible's plugin mechanism.  Thus it raises KeyError on our
    #    helper.* names.
    #
    # 2. Ansible's loaders allow access to the builtin names using unqualified
    #    names (e.g. ``dict2items`` for ``ansible.builtin.dict2items``).  We
    #    don't want to pollute the filter namespace that much.

    def is_fqcn(name: object) -> bool:
        return isinstance(name, str) and name.count(".") >= 2

    env.filters = ChainMap(  # type: ignore[assignment]
        env.filters,
        _FilterKeys(
            map=JinjaPluginIntercept({}, ansible.plugins.loader.filter_loader),
            key_filter=is_fqcn,
        ),
    )
    env.tests = ChainMap(  # type: ignore[assignment]
        env.tests,
        _FilterKeys(
            map=JinjaPluginIntercept({}, ansible.plugins.loader.test_loader),
            key_filter=is_fqcn,
        ),
    )


@dataclass(frozen=True)
class _FilterKeys(MutableMapping[_KT, _VT]):
    """Filter a mapping to mask certain keys.

    This mapping proxies to a ``map``, however any keys that do not
    pass the ``key_filter`` predicate are “filtered out”.

    """

    map: MutableMapping[_KT, _VT]
    key_filter: Callable[[object], bool]

    def __getitem__(self, key: _KT) -> _VT:
        if not self.key_filter(key):
            raise KeyError
        return self.map[key]

    def __setitem__(self, key: _KT, value: _VT) -> None:
        if not self.key_filter(key):
            raise KeyError
        self.map[key] = value

    def __delitem__(self, key: _KT) -> None:
        if not self.key_filter(key):
            raise KeyError
        del self.map[key]

    def __iter__(self) -> Iterator[_KT]:
        return filter(self.key_filter, self.map)

    def __len__(self) -> int:
        return sum(1 for _ in self)

    def __contains__(self, key: object) -> bool:
        # optimization - not required to implement abc
        if not self.key_filter(key):
            return False
        return key in self.map


_need_init = True


def _init_ansible() -> None:
    global _need_init

    if _need_init and hasattr(ansible.plugins.loader, "init_plugin_loader"):
        ansible.plugins.loader.init_plugin_loader()  # ansible-core >= 2.15
    _need_init = False
