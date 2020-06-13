from pathlib import Path
from typing import Any, MutableMapping

import toml

from taskipy.exceptions import (
    MalformedPyProjectError,
    MissingPyProjectFileError,
    MissingTaskipyTasksSectionError
)


class PyProject:
    def __init__(self, file_name: str = "pyproject.toml", directory: Path = Path.cwd()):
        self.path = Path(directory / file_name).resolve()
        self.items = self.__load_toml_file()

    @property
    def tasks(self) -> dict:
        try:
            return self.items["tool"]["taskipy"]["tasks"]
        except KeyError:
            raise MissingTaskipyTasksSectionError()

    @property
    def settings(self) -> dict:
        return self.items["tool"]["taskipy"]["settings"]

    def __load_toml_file(self) -> MutableMapping[str, Any]:
        try:
            return toml.load(self.path)
        except FileNotFoundError:
            raise MissingPyProjectFileError()
        except toml.TomlDecodeError:
            raise MalformedPyProjectError()
