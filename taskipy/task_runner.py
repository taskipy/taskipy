import subprocess
from pathlib import Path
from typing import List, Union

from taskipy.task import Task
from taskipy.pyproject import PyProject


class TaskRunner:
    def __init__(self, pyproject_path: Union[str, Path]):
        self.__pyproject_path = pyproject_path
        self.__project = PyProject(pyproject_path)

    def run(self, task_name: str, args: List[str]) -> int:
        task = Task(task_name, args, self.__project)

        for command in task.commands:
            if task.runner is not None:
                command = f'{task.runner} {command}'

            process = subprocess.Popen(
                command, shell=True, cwd=Path(self.__pyproject_path).parent
            )

            try:
                process.wait()
            except KeyboardInterrupt:
                pass

            if process.returncode != 0:
                return process.returncode

        return 0
