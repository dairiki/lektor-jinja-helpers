from pathlib import Path

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
def renderer(lektor_env: Environment) -> RendererFixture:
    return RendererFixture(lektor_env.jinja_env)
