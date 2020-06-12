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
        """
        Initializes PyProject by setting up the path to and loading in
        the pyproject.toml file in the current directory.

        Args:
            file_name (str, optional): The name of the pyproject file. Defaults to 'pyproject.toml'.
            directory (Path, optional): The directory that the pyproject file is in. Defaults to Path.cwd().
        """
        self.path = Path(directory / file_name).resolve()
        self.items = self.__load_toml_file()

    @property
    def tasks(self) -> dict:
        """Retrieve the taskipy tasks.

        Raises:
            MissingTaskipyTasksSectionError: If there is a missing taskipy tasks section.

        Returns:
            dict: The taskipy tasks.
        """
        try:
            return self.items["tool"]["taskipy"]["tasks"]
        except KeyError:
            raise MissingTaskipyTasksSectionError()

    @property
    def settings(self) -> dict:
        """Retrieve the taskipy settings.

        Returns:
            dict: The taskipy settings.
        """
        return self.items["tool"]["taskipy"]["settings"]

    def __load_toml_file(self) -> MutableMapping[str, Any]:
        """Load in the pyproject file using self.path.

        Raises:
            MissingPyProjectFileError: If the pyproject file is not at path.
            MalformedPyProjectError: If the pyproject file format is invalid.

        Returns:
            dict: The pyproject file.
        """
        try:
            return toml.load(self.path)
        except FileNotFoundError:
            raise MissingPyProjectFileError()
        except toml.TomlDecodeError:
            raise MalformedPyProjectError()
