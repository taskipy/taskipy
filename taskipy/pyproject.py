from pathlib import Path
from typing import Any, MutableMapping

import toml

from taskipy.exceptions import (
    MalformedPyProjectError,
    MissingPyProjectFileError,
    MissingTaskipyTasksSectionError,
    MissingTaskipySettingsSectionError
)


class PyProject:
    def __init__(self, file_name: str = "pyproject.toml", directory: Path = Path.cwd()):
        self.__path = Path(directory / file_name).resolve()
        self.__items = self.__load_toml_file()

    @property
    def tasks(self) -> dict:
        try:
            return self.__items["tool"]["taskipy"]["tasks"]
        except KeyError:
            raise MissingTaskipyTasksSectionError()

    @property
    def settings(self) -> dict:
        try:
            return self.__items["tool"]["taskipy"]["settings"]
        except KeyError:
            raise MissingTaskipySettingsSectionError()

    def __load_toml_file(self) -> MutableMapping[str, Any]:
        try:
            return toml.load(self.__path)
        except FileNotFoundError:
            raise MissingPyProjectFileError()
        except toml.TomlDecodeError:
            raise MalformedPyProjectError()
