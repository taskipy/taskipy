import sys

import psutil  # type: ignore
import signal
import subprocess
from pathlib import Path
from typing import List, Union

from taskipy.pyproject import PyProject
from taskipy.task import Task


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

            def send_signal_to_task_process(signum: int, frame) -> None:  # pylint: disable=unused-argument
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

            signal.signal(signal.SIGTERM, send_signal_to_task_process)

            try:
                process.wait()
            except KeyboardInterrupt:
                pass

            if process.returncode != 0:
                return process.returncode

        return 0
