from typing import Optional

from taskipy.exceptions import MalformedTaskError


class Task:
    def __init__(self, task_name: str, task_toml_contents: object):
        self.__task_name = task_name
        self.__task_command = self.__extract_task_command(task_toml_contents)
        self.__task_description = self.__extract_task_description(task_toml_contents)
        self.__task_use_vars = self.__extract_task_use_vars(task_toml_contents)
        self.__task_workdir = self.__extract_task_workdir(task_toml_contents)

    @property
    def name(self) -> str:
        return self.__task_name

    @property
    def command(self) -> str:
        return self.__task_command

    @property
    def workdir(self) -> Optional[str]:
        return self.__task_workdir

    @property
    def description(self) -> str:
        return self.__task_description

    @property
    def use_vars(self) -> Optional[bool]:
        return self.__task_use_vars

    def __extract_task_use_vars(self, task_toml_contents: object) -> Optional[bool]:
        if isinstance(task_toml_contents, str):
            return None

        if isinstance(task_toml_contents, dict):
            value = task_toml_contents.get('use_vars')
            if value is not None and not isinstance(value, bool):
                raise MalformedTaskError(self.__task_name, f'task\'s "use_vars" arg has to be bool type got {type(value)}')
            return value

        raise MalformedTaskError(self.__task_name, 'tasks must be strings, or dicts that contain { cmd, cwd, help, use_vars }')

    def __extract_task_command(self, task_toml_contents: object) -> str:
        if isinstance(task_toml_contents, str):
            return task_toml_contents

        if isinstance(task_toml_contents, dict):
            try:
                return task_toml_contents['cmd']
            except KeyError:
                raise MalformedTaskError(self.__task_name, 'the task item does not have the "cmd" property')

        raise MalformedTaskError(self.__task_name, 'tasks must be strings, or dicts that contain { cmd, cwd, help, use_vars }')

    def __extract_task_workdir(self, task_toml_contents: object) -> Optional[str]:
        if isinstance(task_toml_contents, str):
            return None

        if isinstance(task_toml_contents, dict):
            try:
                return task_toml_contents['cwd']
            except KeyError:
                return None

        raise MalformedTaskError(self.__task_name, 'tasks must be strings, or dicts that contain { cmd, cwd, help, use_vars }')

    def __extract_task_description(self, task_toml_contents: object) -> str:
        if isinstance(task_toml_contents, str):
            return ''

        if isinstance(task_toml_contents, dict):
            try:
                return task_toml_contents['help']
            except KeyError:
                return ''

        raise MalformedTaskError(self.__task_name, 'tasks must be strings, or dicts that contain { cmd, cwd, help, use_vars }')
