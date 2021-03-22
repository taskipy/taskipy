from argparse import ArgumentParser

class TaskipyError(Exception):
    exit_code = 1


class InvalidRunnerTypeError(TaskipyError):
    def __str__(self):
        return (
            'invalid value: runner is not a string. '
            'please check [tool.taskipy.settings.runner]'
        )


class MissingPyProjectFileError(TaskipyError):
    def __str__(self):
        return 'no pyproject.toml file found in this directory or parent directories'


class MalformedPyProjectError(TaskipyError):
    def __str__(self):
        return 'pyproject.toml file is malformed and could not be read'


class TaskNotFoundError(TaskipyError):
    exit_code = 127

    def __init__(self, task_name: str):
        super().__init__()
        self.task = task_name

    def __str__(self):
        return f'could not find task "{self.task}"'

class InvalidUsageError(TaskipyError):
    exit_code = 127

    def __init__(self, parser: ArgumentParser):
        super().__init__()
        self.__parser = parser

    def __str__(self):
        return self.__parser.format_usage().strip('\n')

class MissingTaskipySettingsSectionError(TaskipyError):
    exit_code = 127

    def __str__(self):
        return (
            'no settings found. add a [tools.taskipy.settings]'
            'section to your pyproject.toml'
        )


class MissingTaskipyTasksSectionError(TaskipyError):
    exit_code = 127

    def __str__(self):
        return (
            'no tasks found. add a [tool.taskipy.tasks] '
            'section to your pyproject.toml'
        )
