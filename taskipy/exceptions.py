class TaskipyError(Exception):
    pass

class TaskNotFoundError(TaskipyError):
    def __init__(self, task_name: str):
        super().__init__()
        self.task = task_name

    def __str__(self):
        return f'could not find task "{self.task}"'


class InvalidRunnerTypeError(TaskipyError):
    def __str__(self):
        return (
            "invalid value: runner is not a string. "
            "please check [tool.taskipy.settings.runner]"
        )


class MissingTaskipyTasksSectionError(TaskipyError):
    def __str__(self):
        return (
            "no tasks found. add a [tool.taskipy.tasks] "
            "section to your pyproject.toml"
        )


class MissingPyProjectFileError(TaskipyError):
    def __str__(self):
        return "no pyproject.toml file found in this directory"


class MalformedPyProjectError(TaskipyError):
    def __str__(self):
        return "pyproject.toml file is malformed and could not be read"
