#!/usr/bin/env python3
import argparse
import subprocess
import sys
import toml
from typing import List

def run_commands_and_bail_on_first_fail(cmds: List[str]) -> int:
    for cmd in cmds:
        p = subprocess.Popen(cmd, shell=True)
        p.wait()
        if p.returncode != 0:
            return p.returncode

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='task')
    parser.add_argument('name', help='name of the task. found in pyproject.toml under [tool.taskify.tasks]')

    args = parser.parse_args()

    try:
        pyproject = toml.load('pyproject.toml')
    except FileNotFoundError:
        print('no pyproject.toml file found in this directory')
        sys.exit(1)
    except:
        print('pyproject.toml file is malformed and could not be read')
        sys.exit(1)

    try:
        tasks = pyproject['tool']['taskify']['tasks']
    except:
        print('no tasks found. add a [tool.taskify.tasks] section to your pyproject.toml')
        sys.exit(127)

    commands = []

    try:
        task = tasks[args.name]
        commands.append(task)
    except:
        print(f'could not find task "{args.name}""')
        sys.exit(127)

    try:
        pre_task = tasks[f'pre_{args.name}']
        commands.insert(0, pre_task)
    except:
        pass

    try:
        post_task = tasks[f'post_{args.name}']
        commands.append(post_task)
    except:
        pass

    exit_code = run_commands_and_bail_on_first_fail(commands)
    sys.exit(exit_code)
    