from typing import Optional

from taskipy.exceptions import (
    InvalidRunnerTypeError,
    TaskNotFoundError,
    MissingTaskipySettingsSectionError
)
from taskipy.pyproject import PyProject


class Task:
    def __init__(self, task_name: str):
        self.project = PyProject()
        self.name = task_name

        try:
            self.command = self.project.tasks[task_name]
        except KeyError:
            raise TaskNotFoundError(self.name)

    def __str__(self) -> str:
        return self.name

    @property
    def pre_task(self) -> Optional[str]:
        try:
            return self.project.tasks[f"pre_{self.name}"]
        except KeyError:
            return None

    @property
    def post_task(self) -> Optional[str]:
        try:
            return self.project.tasks[f"post_{self.name}"]
        except KeyError:
            return None

    @property
    def runner(self) -> Optional[str]:
        try:
            runner = self.project.settings["runner"]

            if not isinstance(runner, str):
                raise InvalidRunnerTypeError()

            return runner.strip()
        except (KeyError, MissingTaskipySettingsSectionError):
            return None
