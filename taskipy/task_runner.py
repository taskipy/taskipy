import shlex
import subprocess
from pathlib import Path
from typing import List

from taskipy.task import Task


class TaskRunner:
    def __init__(self, task_name: str, args: List[str]):
        """
        Task Runner is what handles running the task from the cli arguments.

        It is initialized by retrieving the command to run from the given task_name
        and adding that commands, with any arguments, into the commands to run later.

        Args:
            task_name (str): The name of the task to run from [tools.taskipy.tasks].
            args (List[str]): The arguments passed in to that command.
        """
        self.task = Task(task_name)
        self.commands = []
        self.commands.append(
            " ".join([self.task.command] + [shlex.quote(arg) for arg in args])
        )

    def run(self) -> int:
        """
        Sets up the order of the commands to be
        executed if there are any pre/post tasks
        and then runs the commands, bailing on the
        first fail.

        Returns:
            int: The return code of the last task that ran.
                 0 if all tasks succeeded; > 0 on fail.
        """
        if self.task.pre_task:
            self.commands.insert(0, self.task.pre_task)

        if self.task.post_task:
            self.commands.append(self.task.post_task)

        return self.__run_commands_and_bail_on_first_fail()

    def __run_commands_and_bail_on_first_fail(self) -> int:
        """
        Runs the commands and returns a non-zero
        exit code on the first fail.

        Returns:
            int: The return code of the last task that ran.
                 0 if all tasks succeeded; > 0 on fail.
        """
        for cmd in self.commands:
            if self.task.runner is not None:
                cmd = f"{self.task.runner} {cmd}"

            process = subprocess.Popen(cmd, shell=True, cwd=Path.cwd())

            try:
                process.wait()
            except KeyboardInterrupt:
                pass

            if process.returncode != 0:
                return process.returncode

        return 0
