import sys
import platform
import psutil  # type: ignore
import signal
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional

from taskipy.pyproject import PyProject
from taskipy.exceptions import CircularVariableError, TaskNotFoundError, MalformedTaskError
from taskipy.task import Task
from taskipy.help import HelpFormatter
from taskipy.variable import Variable

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
                command = self.__resolve_variables(command)
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

    def __resolve_variables(self, command: str) -> str:
        types = self.__get_variable_types(self.__project.variables)
        resolved_vars = types["nonrecursive"]
        recursive_vars = types["recursive"]

        while len(recursive_vars) > 0:
            count_of_previously_resolved_vars = len(resolved_vars)

            for name, value in recursive_vars.copy().items():
                try:
                    resolved_vars[name] = value.format(**resolved_vars)
                    recursive_vars.pop(name)
                except KeyError:
                    pass

            if count_of_previously_resolved_vars == len(resolved_vars):
                raise CircularVariableError()

        return command.format(**resolved_vars)

    def __get_variable_types(self, variables: Dict[str, Variable]) -> Dict[str, Dict[str, str]]:
        var_types: Dict[str, Dict[str, str]] = {
            "nonrecursive": {},
            "recursive": {}
        }

        for name, var in variables.items():
            if var.recursive:
                var_types["recursive"][name] = var.value
            else:
                var_types["nonrecursive"][name] = var.value

        return var_types
