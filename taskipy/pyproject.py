import toml

from pathlib import Path
from typing import Any, MutableMapping, Optional, Union

from taskipy.task import Task
from taskipy.exceptions import (
    InvalidRunnerTypeError,
    MalformedPyProjectError,
    MissingPyProjectFileError,
    MissingTaskipyTasksSectionError,
    MissingTaskipySettingsSectionError
)


class PyProject:
    def __init__(self, base_dir: Path):
        pyproject_path = self.__find_pyproject_path(base_dir)
        self.__items = PyProject.__load_toml_file(pyproject_path)

    @property
    def tasks(self) -> dict[str, Task]:
        try:
            return {
                task_name: Task(task_name, task_toml_contents) for
                task_name, task_toml_contents in self.__items['tool']['taskipy']['tasks'].items() }
        except KeyError:
            raise MissingTaskipyTasksSectionError()

    @property
    def settings(self) -> dict:
        try:
            return self.__items['tool']['taskipy']['settings']
        except KeyError:
            raise MissingTaskipySettingsSectionError()

    @property
    def runner(self) -> Optional[str]:
        try:
            runner = self.settings['runner']

            if not isinstance(runner, str):
                raise InvalidRunnerTypeError()

            return runner.strip()
        except (KeyError, MissingTaskipySettingsSectionError):
            return None

    @staticmethod
    def __load_toml_file(file_path: Union[str, Path]) -> MutableMapping[str, Any]:
        try:
            if isinstance(file_path, str):
                file_path = Path(file_path).resolve()

            return toml.load(file_path)
        except FileNotFoundError:
            raise MissingPyProjectFileError()
        except toml.TomlDecodeError:
            raise MalformedPyProjectError()

    @staticmethod
    def __find_pyproject_path(base_dir: Path) -> Path:
        def candidate_dirs(base: Path):
            yield base
            for parent in base.parents:
                yield parent
        for candidate_dir in candidate_dirs(base_dir):
            pyproject = candidate_dir / 'pyproject.toml'
            if pyproject.exists():
                return pyproject
        raise MissingPyProjectFileError()
