import tempfile
import shutil
import os
from os import path
from abc import abstractmethod

class ProjectDirGenerator:
    @abstractmethod
    def generate_project(self, temp_dir: str):
        pass


class GenerateProjectFromFixture(ProjectDirGenerator):
    def __init__(self, fixture_dir: str):
        self._fixture_dir: str = fixture_dir

    def generate_project(self, temp_dir: str):
        shutil.copytree(self._fixture_dir, temp_dir)


class GenerateProjectWithPyProjectToml(ProjectDirGenerator):
    def __init__(self, py_project_toml: str):
        self._py_project_toml: str = py_project_toml

    def generate_project(self, temp_dir: str):
        os.makedirs(temp_dir)
        with open(path.join(temp_dir, 'pyproject.toml'), 'w', encoding='utf-8') as f:
            f.write(self._py_project_toml)


class TempProjectDir:
    def __init__(self, project_dir_generator: ProjectDirGenerator):
        self._tmpdir: str = tempfile.mktemp()
        project_dir_generator.generate_project(self._tmpdir)

    @property
    def path(self):
        return self._tmpdir

    def clean(self):
        shutil.rmtree(self._tmpdir, ignore_errors=True)
