import sys
import platform
import psutil  # type: ignore
import signal
import string
import subprocess
from pathlib import Path
from typing import List, Tuple, Union, Optional

from taskipy.pyproject import PyProject
from taskipy.exceptions import TaskNotFoundError, MalformedTaskError
from taskipy.task import Task
from taskipy.help import HelpFormatter

if platform.system() == 'Windows':
    import mslex as shlex  # type: ignore # pylint: disable=E0401
else:
    import shlex  # type: ignore[no-redef]


class TaskRunner:
    def __init__(self, cwd: Union[str, Path]):
        working_dir = cwd if isinstance(cwd, Path) else Path(cwd)
        self.__working_dir = working_dir
        self.__project = PyProject(working_dir)

    def list(self):
        """lists tasks to stdout"""
        formatter = HelpFormatter(self.__project.tasks.values())
        formatter.print()

    def run(self, task_name: str, task_args: List[str]) -> int:
        try:
            main_task = self.__project.tasks[task_name]
        except KeyError:
            raise TaskNotFoundError(task_name)

        tasks: List[Tuple[Optional[Task], List[str]]] = [
            (self.__pre_task(task_name), []),
            (main_task, task_args),
            (self.__post_task(task_name), []),
        ]
        for task, args in tasks:
            if task is None:
                continue

            exit_code = self.__execute_command(task, args)
            if exit_code != 0:
                return exit_code

        return 0

    def __pre_task(self, task_name: str) -> Optional[Task]:
        return self.__project.tasks.get(f'pre_{task_name}')

    def __post_task(self, task_name: str) -> Optional[Task]:
        return self.__project.tasks.get(f'post_{task_name}')

    def __execute_command(self, task: Task, args: Optional[List[str]] = None) -> int:
        if args is None:
            args = []

        command = task.command
        if task.use_vars or self.__project.settings.get('use_vars'):
            try:
                command = self.__expand_variables(command)
            except KeyError as e:
                raise MalformedTaskError(task.name, f'{e} variable expected in [tool.taskipy.variables]')

        if self.__project.runner is not None:
            command = f'{self.__project.runner} {command}'

        def send_signal_to_task_process(signum: int, _frame) -> None:
            # pylint: disable=W0640
            psutil_process_wrapper = psutil.Process(process.pid)
            is_direct_subprocess_a_shell_process = sys.platform != 'darwin'  # pylint: disable=C0103

            if is_direct_subprocess_a_shell_process:
                # A shell is created because of Popen(..., shell=True) on linux only
                # We want here to kill shell's child
                sub_processes_of_taskipy_shell = psutil_process_wrapper.children()
                for child_process in sub_processes_of_taskipy_shell:
                    child_process.send_signal(signum)
            else:
                process.send_signal(signum)

        command_with_args = ' '.join([command] + [shlex.quote(arg) for arg in args])
        process = subprocess.Popen(command_with_args,
                                   shell=True,
                                   cwd=self.__working_dir)
        signal.signal(signal.SIGTERM, send_signal_to_task_process)

        try:
            process.wait()
        except KeyboardInterrupt:
            pass

        return process.returncode

    def __expand_variables(self, command: str) -> str:
        placeholders = self.__get_format_placeholders(command)

        if len(placeholders) == 0:
            return command

        return self.__expand_variables(command.format(**self.__project.variables))

    def __get_format_placeholders(self, format_string: str) -> List[str]:
        placeholders = []

        for result in string.Formatter().parse(format_string):
            if result[1] is not None:
                placeholders.append(result[1])

        return placeholders
