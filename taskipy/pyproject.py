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
    def __init__(self, file_path: Union[str, Path]):
        self.__items = PyProject.__load_toml_file(file_path)

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
