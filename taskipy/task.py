from taskipy.exceptions import InvalidRunnerTypeError, TaskNotFoundError
from taskipy.pyproject import PyProject


class Task:
    def __init__(self, task_name: str):
        self.project = PyProject()
        self.name = task_name

        try:
            self.command = self.project.tasks[task_name]
        except KeyError:
            raise TaskNotFoundError(self.name)

    def __str__(self):
        return self.name

    @property
    def pre_task(self):
        try:
            return self.project.tasks[f"pre_{self.name}"]
        except KeyError:
            return None

    @property
    def post_task(self):
        try:
            return self.project.tasks[f"post_{self.name}"]
        except KeyError:
            return None

    @property
    def runner(self):
        try:
            return self.project.settings["runner"].strip()
        except KeyError:
            return None
        except AttributeError:
            raise InvalidRunnerTypeError()
