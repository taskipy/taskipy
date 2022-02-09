import tomli

from pathlib import Path
from typing import Any, Dict, MutableMapping, Optional, Union

from taskipy.task import Task
from taskipy.exceptions import (
    InvalidRunnerTypeError,
    MalformedPyProjectError,
    MissingPyProjectFileError,
    MissingTaskipyTasksSectionError
)
from taskipy.variable import Variable


class PyProject:
    def __init__(self, base_dir: Path):
        pyproject_path = self.__find_pyproject_path(base_dir)
        self.__items = self.__load_toml_file(pyproject_path)

    @property
    def tasks(self) -> Dict[str, Task]:
        try:
            toml_tasks = self.__items['tool']['taskipy']['tasks'].items()
        except KeyError:
            raise MissingTaskipyTasksSectionError()

        tasks = {}
        for name, toml_contents in toml_tasks:
            tasks[name] = Task(name, toml_contents)

        return tasks

    @property
    def variables(self) -> Dict[str, Variable]:
        try:
            toml_vars = self.__items['tool']['taskipy'].get('variables', {})
        except KeyError:
            return {}

        vars_dict: Dict[str, Variable] = {}
        for name, toml_contents in toml_vars.items():
            if isinstance(toml_contents, str):
                vars_dict[name] = Variable(name, toml_contents, recursive=False)
            elif toml_contents.get('var') or toml_contents.get('recursive'):
                vars_dict[name] = Variable(
                    name,
                    toml_contents.get('var'),
                    toml_contents.get('recursive', False),
                )

        return vars_dict

    @property
    def settings(self) -> dict:
        try:
            return self.__items['tool']['taskipy']['settings']
        except KeyError:
            return {}

    @property
    def runner(self) -> Optional[str]:
        try:
            runner = self.settings['runner']

            if not isinstance(runner, str):
                raise InvalidRunnerTypeError()

            return runner.strip()
        except KeyError:
            return None

    @staticmethod
    def __load_toml_file(file_path: Union[str, Path]) -> MutableMapping[str, Any]:
        try:
            if isinstance(file_path, str):
                file_path = Path(file_path).resolve()

            with open(file_path, 'rb') as file:
                return tomli.load(file)
        except FileNotFoundError:
            raise MissingPyProjectFileError()
        except tomli.TOMLDecodeError as e:
            raise MalformedPyProjectError(reason=str(e))

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
