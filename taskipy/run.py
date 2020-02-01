import os
import subprocess
import sys
import toml
from os import path
from typing import List

def run_task(task_name: str, args: List[str], cwd=os.curdir):
    def run_commands_and_bail_on_first_fail(cmds: List[str]) -> int:
        for cmd in cmds:
            p = subprocess.Popen(cmd, shell=True, cwd=cwd)

            try:
                p.wait()
            except KeyboardInterrupt:
                pass

            if p.returncode != 0:
                return p.returncode

        return 0

    try:
        pyproject = toml.load(path.join(cwd, 'pyproject.toml'))
    except FileNotFoundError:
        print('no pyproject.toml file found in this directory')
        sys.exit(1)
    except toml.TomlDecodeError:
        print('pyproject.toml file is malformed and could not be read')
        sys.exit(1)

    try:
        tasks = pyproject['tool']['taskipy']['tasks']
    except KeyError:
        print('no tasks found. add a [tool.taskipy.tasks] section to your pyproject.toml')
        sys.exit(127)

    commands = []

    try:
        task = tasks[task_name]
    except KeyError:
        print(f'could not find task "{task_name}""')
        sys.exit(127)

    command_with_passed_args = ' '.join([task] + args)
    commands.append(command_with_passed_args)

    try:
        pre_task = tasks[f'pre_{task_name}']
        commands.insert(0, pre_task)
    except KeyError:
        pass

    try:
        post_task = tasks[f'post_{task_name}']
        commands.append(post_task)
    except KeyError:
        pass

    exit_code = run_commands_and_bail_on_first_fail(commands)
    sys.exit(exit_code)
