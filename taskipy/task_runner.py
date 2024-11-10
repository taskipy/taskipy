import sys
import platform
import signal
import subprocess
from difflib import get_close_matches
from pathlib import Path
from types import FrameType
from typing import Callable, Dict, List, Tuple, Union, Optional

import psutil  # type: ignore

from taskipy.exceptions import CircularVariableError, TaskNotFoundError, MalformedTaskError
from taskipy.list import TasksListFormatter
from taskipy.pyproject import PyProject
from taskipy.task import Task
from taskipy.variable import Variable

if platform.system() == 'Windows':
    import mslex as shlex  # type: ignore # pylint: disable=E0401
else:
    import shlex  # type: ignore[no-redef]


class TaskRunner:
    def __init__(self, cwd: Union[str, Path]):
        cwd_as_path = cwd if isinstance(cwd, Path) else Path(cwd)
        self.__project = PyProject(cwd_as_path)
        self.__working_dir = self.__get_working_dir() or cwd_as_path

    def list(self):
        """lists tasks to stdout"""
        formatter = TasksListFormatter(self.__project.tasks.values())
        formatter.print()

    def run(self, task_name: str, args: List[str]) -> int:
        subtasks = self.__get_subtasks(task_name)
        if not subtasks:
            return self.__run_commands(task_name, args)
        result: int = 1
        for subtask in subtasks:
            if subtask:
                result = self.__run_commands(subtask, None)
        return result

    def __run_commands(self, task_name: str, args: List[str] | None) -> int:
        pre_command, command, post_command = self.__get_formatted_commands(task_name)
        self.__working_dir =  self.__get_working_dir(task_name) or self.__working_dir

        if pre_command is not None:
            exit_code = self.__run_command_and_return_exit_code(pre_command)
            if exit_code != 0:
                return exit_code

        exit_code = self.__run_command_and_return_exit_code(command, args)
        if exit_code != 0:
            return exit_code

        if post_command is not None:
            exit_code = self.__run_command_and_return_exit_code(post_command)
            if exit_code != 0:
                return exit_code

        return 0

    def __get_formatted_commands(
        self, task_name: str
    ) -> Tuple[Optional[str], str, Optional[str]]:
        pre_task, task, post_task = self.__get_tasks(task_name)

        should_resolve_vars = (
            self.__is_using_vars([pre_task, task, post_task])
            or self.__project.settings.get('use_vars') is True
        )
        variables = self.__resolve_variables() if should_resolve_vars else {}

        pre_command = None
        if pre_task is not None:
            pre_command = self.__format_task_command(pre_task, variables)

        command: str = ''
        if task.command:
            command = self.__format_task_command(task, variables)

        post_command = None
        if post_task is not None:
            post_command = self.__format_task_command(post_task, variables)

        return pre_command, command, post_command

    def __get_subtasks(self, task_name: str) -> List[str] | None:
        task_config = self.__project.tasks.get(task_name)
        if task_config:
            return task_config.subtasks
        return None

    def __get_tasks(self, task_name: str) -> Tuple[Optional[Task], Task, Optional[Task]]:
        pre_task = self.__pre_task(task_name)
        post_task = self.__post_task(task_name)

        try:
            task = self.__project.tasks[task_name]
        except KeyError:
            suggestion = None
            closest_match = get_close_matches(task_name, self.__project.tasks, n=1, cutoff=0.5)

            if closest_match:
                suggestion = closest_match[0]
            raise TaskNotFoundError(task_name, suggestion)

        return pre_task, task, post_task

    def __pre_task(self, task_name: str) -> Optional[Task]:
        return self.__project.tasks.get(f'pre_{task_name}')

    def __post_task(self, task_name: str) -> Optional[Task]:
        return self.__project.tasks.get(f'post_{task_name}')

    def __is_using_vars(self, tasks: List[Optional[Task]]) -> bool:
        use_vars = False

        for task in tasks:
            if task is not None and task.use_vars:
                use_vars = True
                break

        return use_vars

    def __resolve_variables(self) -> Dict[str, str]:
        nonrecursive_vars, recursive_vars = self.__get_variable_types(
            self.__project.variables
        )

        while len(recursive_vars) > 0:
            count_of_previously_resolved_vars = len(nonrecursive_vars)  # pylint: disable=C0103

            for name, value in recursive_vars.copy().items():
                try:
                    nonrecursive_vars[name] = value.format(**nonrecursive_vars)
                    recursive_vars.pop(name)
                except KeyError:
                    pass

            if count_of_previously_resolved_vars == len(nonrecursive_vars):
                raise CircularVariableError()

        return nonrecursive_vars

    def __get_variable_types(
        self, variables: Dict[str, Variable]
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
        nonrecursive_vars = {}
        recursive_vars = {}

        for name, var in variables.items():
            if var.recursive:
                recursive_vars[name] = var.value
            else:
                nonrecursive_vars[name] = var.value

        return nonrecursive_vars, recursive_vars

    def __format_task_command(self, task: Task, variables: dict) -> str:
        if not task.command:
            raise MalformedTaskError(
                task.name,
                f'command expected in task {task}'
            )

        if task.use_vars or (
            task.use_vars is None and self.__project.settings.get('use_vars')
        ):
            try:
                return task.command.format(**variables)
            except KeyError as e:
                raise MalformedTaskError(
                    task.name,
                    f'{e} variable expected in [tool.taskipy.variables]',
                )

        return task.command

    def __run_command_and_return_exit_code(
        self, command: str, args: Optional[List[str]] = None
    ) -> int:
        if args is None:
            args = []

        if self.__project.runner is not None:
            command = f'{self.__project.runner} {command}'

        command_with_args = ' '.join([command] + [shlex.quote(arg) for arg in args])
        process = subprocess.Popen(
            command_with_args, shell=True, cwd=self.__working_dir
        )
        signal.signal(signal.SIGTERM, self.__send_signal_to_task_process(process))

        try:
            process.wait()
        except KeyboardInterrupt:
            pass

        return process.returncode

    def __send_signal_to_task_process(
        self, process: subprocess.Popen
    ) -> Callable[[int, Optional[FrameType]], None]:
        def signal_handler(signum: int, _frame):
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

        return signal_handler

    def __get_working_dir(self, task_name: Optional[str] = None) -> Optional[Path]:
        cwd: Optional[str] = self.__project.settings.get("cwd", None)

        if task_name is not None:
            cwd = self.__project.tasks[task_name].workdir or cwd

        if cwd is not None:
            path = self.__project.dirpath / cwd
            if path.exists():
                return path

        return None
