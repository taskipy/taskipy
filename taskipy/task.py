from typing import Optional

from taskipy.exceptions import InvalidRunnerTypeError, TaskNotFoundError
from taskipy.pyproject import PyProject


class Task:
    def __init__(self, task_name: str):
        """
        Sets up the task by saving it's name and
        retrieiving the command it references in the
        pyproject file.

        Args:
            task_name (str): The name of the task in [tools.taskipy.tasks].

        Raises:
            TaskNotFoundError: If the task could not be found in the
                               [tools.taskipy.tasks] section.
        """
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
        """
        Retrieves the pre task of the given task.

        Returns:
            str or None: The pre task, if it exists.
        """
        try:
            return self.project.tasks[f"pre_{self.name}"]
        except KeyError:
            return None

    @property
    def post_task(self) -> Optional[str]:
        """
        Retrieves the post task of the given task.

        Returns:
            str or None: The post task, if it exists.
        """
        try:
            return self.project.tasks[f"post_{self.name}"]
        except KeyError:
            return None

    @property
    def runner(self) -> Optional[str]:
        """
        Retrieves what runner to use for this task
        from [tools.taskipy.settings.runner].

        Raises:
            InvalidRunnerTypeError: If the type of the runner value is not a string.

        Returns:
            str or None: The runner to use, if it is set.
        """
        try:
            return self.project.settings["runner"].strip()
        except KeyError:
            return None
        except AttributeError:
            raise InvalidRunnerTypeError()
