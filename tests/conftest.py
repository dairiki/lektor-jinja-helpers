import pytest
from lektor.environment import Environment
from lektor.project import Project

from .testlib import RendererFixture


@pytest.fixture(scope="session")
def lektor_env(tmp_path_factory: pytest.TempPathFactory) -> Environment:
    tmp_path = tmp_path_factory.mktemp("project")
    project_file = tmp_path / "test.lektorproject"
    project_file.touch()
    project = Project.from_file(project_file)
    return project.make_env()


@pytest.fixture
def renderer(lektor_env: Environment) -> RendererFixture:
    return RendererFixture(lektor_env.jinja_env)
