#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from taskipy.exceptions import TaskipyError
from taskipy.task_runner import TaskRunner


def main():
    parser = argparse.ArgumentParser(
        prog='task',
        description='runs a task specified in your pyproject.toml under [tool.taskipy.tasks]',
    )
    parser.add_argument('--list', help='show list of available tasks', action='store_true')
    parser.add_argument('name', help='name of the task', nargs='?')
    parser.add_argument('args', nargs='*', help='arguments to pass to the task')
    args = parser.parse_args()
    try:
        runner = TaskRunner(Path.cwd() / 'pyproject.toml')
        if args.list:
            longest = len(max(runner.project.tasks, key=len))
            for k, v in runner.project.tasks.items():
                print(f'{k:<{longest}}  {v}')
            sys.exit(0)
        exit_code = runner.run(args.name, args.args)
        sys.exit(exit_code)
    except TaskipyError as e:
        print(e)
        sys.exit(e.exit_code)
    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
