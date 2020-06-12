import shlex
import subprocess
from pathlib import Path
from typing import List

from taskipy.task import Task


class TaskRunner:
    def __init__(self, task_name: str, args: List[str]):
        self.task = Task(task_name)
        self.commands = []
        self.commands.append(
            " ".join([self.task.command] + [shlex.quote(arg) for arg in args])
        )

    def run(self):
        if self.task.pre_task:
            self.commands.insert(0, self.task.pre_task)

        if self.task.post_task:
            self.commands.append(self.task.post_task)

        return self.__bail_on_first_fail(self.commands, runner=self.task.runner)

    def __bail_on_first_fail(self, cmds: List[str], runner: str = None) -> int:
        for cmd in cmds:
            if runner is not None:
                cmd = f"{runner} {cmd}"

            process = subprocess.Popen(cmd, shell=True, cwd=Path.cwd())

            try:
                process.wait()
            except KeyboardInterrupt:
                pass

            if process.returncode != 0:
                return process.returncode

        return 0
