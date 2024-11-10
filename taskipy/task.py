from typing import Optional

from taskipy.exceptions import MalformedTaskError


class Task:
    def __init__(self, task_name: str, task_toml_contents: object):
        self.__task_name = task_name
        self.__task_command = self.__extract_task_command(task_toml_contents)
        self.__task_description = self.__extract_task_description(task_toml_contents)
        self.__task_subtasks = self.__extract_task_subtasks(task_toml_contents)
        self.__task_use_vars = self.__extract_task_use_vars(task_toml_contents)
        self.__task_workdir = self.__extract_task_workdir(task_toml_contents)

    @property
    def name(self) -> str:
        return self.__task_name

    @property
    def command(self) -> Optional[str]:
        return self.__task_command

    @property
    def workdir(self) -> Optional[str]:
        return self.__task_workdir

    @property
    def description(self) -> str:
        return self.__task_description

    @property
    def subtasks(self) -> Optional[list[str]]:
        return self.__task_subtasks

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

        raise MalformedTaskError(self.__task_name, 'tasks must be strings, or dicts that contain { cmd, cwd, help, subtasks, use_vars }')

    def __extract_task_command(self, task_toml_contents: object) -> Optional[str]:
        if isinstance(task_toml_contents, str):
            return task_toml_contents

        if not isinstance(task_toml_contents, dict):
            raise MalformedTaskError(self.__task_name, 'tasks must be strings, or dicts that contain { cmd, cwd, help, subtasks, use_vars }')

        if "cmd" in task_toml_contents and "subtasks" in task_toml_contents:
            raise MalformedTaskError(self.__task_name, 'the task item must include "cmd" or "subtasks". Never both.')

        if "subtasks" in task_toml_contents:
            return None

        try:
            return task_toml_contents['cmd']
        except KeyError:
            raise MalformedTaskError(self.__task_name, 'the task item does not have the "cmd" property')

    def __extract_task_workdir(self, task_toml_contents: object) -> Optional[str]:
        if isinstance(task_toml_contents, str):
            return None

        if isinstance(task_toml_contents, dict):
            value = task_toml_contents.get('cwd')
            if value is not None and not isinstance(value, str):
                raise MalformedTaskError(self.__task_name, f'task\'s "cwd" arg has to be str type got {type(value)}')
            return value

        raise MalformedTaskError(
            self.__task_name,
            'tasks must be strings, or dicts that contain { cmd, cwd, help, subtasks, use_vars }'
        )

    def __extract_task_description(self, task_toml_contents: object) -> str:
        if isinstance(task_toml_contents, str):
            return ''

        if isinstance(task_toml_contents, dict):
            try:
                return task_toml_contents['help']
            except KeyError:
                return ''

        raise MalformedTaskError(
            self.__task_name,
            'tasks must be strings, or dicts that contain { cmd, cwd, help, subtasks, use_vars }'
        )

    def __extract_task_subtasks(self, task_toml_contents: object) -> Optional[list[str]]:
        if isinstance(task_toml_contents, str):
            return None

        if not isinstance(task_toml_contents, dict):
            raise MalformedTaskError(
                self.__task_name,
                'tasks must be strings, or dicts that contain { cmd, cwd, help, subtasks, use_vars }'
            )

        value = task_toml_contents.get('subtasks')
        if value is None:
            return None

        if not isinstance(value, list):
            raise MalformedTaskError(
                self.__task_name,
                f'task\'s "subtasks" arg has to be list[str] type got {type(value)}'
            )

        invalid_items = [item for item in value if not isinstance(item, str)]
        if invalid_items:
            raise MalformedTaskError(
                self.__task_name,
                f'task\'s "subtasks" arg has to be list[str]. Got {invalid_items}'
            )
        return value
