from __future__ import annotations

from collections import ChainMap
from typing import Any
from typing import Iterator
from typing import MutableMapping

import jinja2

try:
    import ansible.plugins.loader
    from ansible.template import JinjaPluginIntercept
except ModuleNotFoundError:
    ansible = None


def import_ansible_filters_and_tests(env: jinja2.Environment) -> None:
    """Monkeypatch Jinja environment to make Ansible filters and tests availabled."""
    if ansible is None:
        return  # ansible is not installed
    if _is_our_chainmap(env.filters):
        return  # we've already monkey-patched the jinja environment

    assert type(env.filters) is dict
    assert type(env.tests) is dict

    _init_ansible()

    env.filters = ChainMap(  # type: ignore[assignment]
        env.filters,
        _AnsibleLookup(ansible.plugins.loader.filter_loader),
    )
    env.tests = ChainMap(  # type: ignore[assignment]
        env.tests,
        _AnsibleLookup(ansible.plugins.loader.test_loader),
    )


class _AnsibleLookup(MutableMapping[str, Any]):
    """Mapping view of filters or tests from Ansible loader.

    Notes
    ^^^^^

    Ansible normally monkey-patches a JinjaPluginIntercept instance
    directly into jinja's env.filters and env.tests.

    We can't use JinjaPluginIntercept directly for two reasons:

    1. JinjaPluginIntercept tries to load any dotted name via
       Ansible's plugin mechanism.  Thus it raises KeyError on our
       helper.* names.

    2. Ansible's loaders allow access to the builtin names using unqualified
       names (e.g. ``dict2items`` for ``ansible.builtin.dict2items``).  We
       don't want to pollute the filter namespace that much.

    """

    def __init__(self, loader: ansible.plugins.loader.Jinja2Loader):
        self.data = JinjaPluginIntercept({}, loader)

    def __getitem__(self, key: str) -> Any:
        if key.count(".") >= 2:
            # only allow access to fully qualified names
            return self.data[key]
        raise KeyError()

    def __setitem__(self, key: str, value: Any) -> None:
        raise NotImplementedError()

    def __delitem__(self, key: str) -> None:
        raise NotImplementedError()

    def __iter__(self) -> Iterator[Any]:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def __contains__(self, key: object) -> bool:
        if isinstance(key, str) and key.count(".") >= 2:
            return key in self.data
        return False


def _is_our_chainmap(obj: object) -> bool:
    return isinstance(obj, ChainMap) and isinstance(obj.maps[1], JinjaPluginIntercept)


_need_init = True


def _init_ansible() -> None:
    global _need_init

    if _need_init and hasattr(ansible.plugins.loader, "init_plugin_loader"):
        ansible.plugins.loader.init_plugin_loader()  # ansible-core >= 2.15
    _need_init = False
