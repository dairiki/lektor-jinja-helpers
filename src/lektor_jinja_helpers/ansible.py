from __future__ import annotations

from collections import ChainMap

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

    ansible_filters = JinjaPluginIntercept(
        env.filters, ansible.plugins.loader.filter_loader
    )
    # Ansible monkey-patches env.filters to ansible_filters, however
    # the JinjaPluginIntercept always tries to re/load dotted names
    # (e.g. raising KeyError on our 'helpers.excerpt_html').
    # So ChainMap the original filters dict in front of ansible_filters.
    env.filters = ChainMap(env.filters, ansible_filters)  # type: ignore[assignment]

    ansible_tests = JinjaPluginIntercept(env.tests, ansible.plugins.loader.test_loader)
    env.tests = ChainMap(env.tests, ansible_tests)  # type: ignore[assignment]


def _is_our_chainmap(obj: object) -> bool:
    return isinstance(obj, ChainMap) and isinstance(obj.maps[1], JinjaPluginIntercept)


_need_init = True


def _init_ansible() -> None:
    global _need_init

    if _need_init and hasattr(ansible.plugins.loader, "init_plugin_loader"):
        ansible.plugins.loader.init_plugin_loader()  # ansible-core >= 2.15
    _need_init = False
