class TaskipyError(Exception):
    """
    A generic Taskipy exception that all exceptions inherit from.

    This allows you do catch a TaskipyError, and it will catch
    all exceptions that come from Taskipy.
    """


class TaskNotFoundError(TaskipyError):
    """
    A exception for when the task searched
    for in [tools.taskipy.tasks] is not found.
    """

    def __init__(self, task_name: str):
        super().__init__()
        self.task = task_name

    def __str__(self):
        return f'could not find task "{self.task}"'


class InvalidRunnerTypeError(TaskipyError):
    """
    A exception for when the [tool.taskipy.settings.runner]
    type is not a string.
    """

    def __str__(self):
        return (
            "invalid value: runner is not a string. "
            "please check [tool.taskipy.settings.runner]"
        )


class MissingTaskipyTasksSectionError(TaskipyError):
    """
    A exception for when there is not a
    [tool.taskipy.tasks] section.
    """

    def __str__(self):
        return (
            "no tasks found. add a [tool.taskipy.tasks] "
            "section to your pyproject.toml"
        )


class MissingPyProjectFileError(TaskipyError):
    """
    A exception for when there is no pyproject.toml
    file in the current directory.
    """

    def __str__(self):
        return "no pyproject.toml file found in this directory"


class MalformedPyProjectError(TaskipyError):
    """
    A exception for when the pyproject.toml file is malformed.
    """

    def __str__(self):
        return "pyproject.toml file is malformed and could not be read"
