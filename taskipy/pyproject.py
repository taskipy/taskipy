from pathlib import Path
from typing import Any, MutableMapping, Union

import toml

from taskipy.exceptions import (
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
    def tasks(self) -> dict:
        try:
            return self.__items['tool']['taskipy']['tasks']
        except KeyError:
            raise MissingTaskipyTasksSectionError()

    @property
    def settings(self) -> dict:
        try:
            return self.__items['tool']['taskipy']['settings']
        except KeyError:
            raise MissingTaskipySettingsSectionError()

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
