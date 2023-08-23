from pathlib import Path

import jinja2
import pytest
from lektor.db import Pad
from lektor.environment import Environment
from lektor.project import Project

from .testlib import RendererFixture


@pytest.fixture(scope="session")
def lektor_env() -> Environment:
    here = Path(__file__).parent
    project = Project.from_file(here / "test-project/test.lektorproject")
    return project.make_env()


@pytest.fixture(scope="session")
def lektor_pad(lektor_env: Environment) -> Pad:
    return lektor_env.new_pad()


@pytest.fixture
def jinja_env(lektor_env: Environment) -> jinja2.Environment:
    return lektor_env.jinja_env  # type: ignore[no-any-return]


@pytest.fixture
def renderer(jinja_env: jinja2.Environment) -> RendererFixture:
    return RendererFixture(jinja_env)
