import platform
import shlex
import mslex # type: ignore
from typing import Optional, List

from taskipy.exceptions import (
    InvalidRunnerTypeError,
    TaskNotFoundError,
    MissingTaskipySettingsSectionError
)
from taskipy.pyproject import PyProject


class Command:
    def __init__(self, task_name: str, args: List[str], project: PyProject):
        self.project = project
        self.name = task_name
        self.args = args

    def __str__(self) -> str:
        return self.name

    @property
    def pre_task(self) -> Optional[str]:
        return self.__find_hooks('pre')

    @property
    def post_task(self) -> Optional[str]:
        return self.__find_hooks('post')

    @property
    def commands(self) -> List[str]:
        try:
            command = self.project.tasks[self.name]
            commands = []
            commands.append(
                ' '.join([command] + [self.__quote_arg(arg) for arg in self.args])
            )

            if self.pre_task:
                commands.insert(0, self.pre_task)

            if self.post_task:
                commands.append(self.post_task)

            return commands
        except KeyError:
            raise TaskNotFoundError(self.name)

    @property
    def runner(self) -> Optional[str]:
        try:
            runner = self.project.settings['runner']

            if not isinstance(runner, str):
                raise InvalidRunnerTypeError()

            return runner.strip()
        except (KeyError, MissingTaskipySettingsSectionError):
            return None

    def __find_hooks(self, hook_type: str) -> Optional[str]:
        try:
            return self.project.tasks[f'{hook_type}_{self.name}']
        except KeyError:
            return None

    def __quote_arg(self, arg: str) -> str:
        if platform.system() == 'Windows':
            return mslex.quote(arg)
        return shlex.quote(arg)
