#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from typing import List, Optional

from taskipy.exceptions import TaskipyError, InvalidUsageError
from taskipy.task_runner import TaskRunner


def main():
    parser = argparse.ArgumentParser(
        prog='task',
        description='runs a task specified in your pyproject.toml under [tool.taskipy.tasks]',
    )
    parser.add_argument('-l', '--list', help='show list of available tasks', action='store_true')
    parser.add_argument('name', help='name of the task', nargs='?')
    parser.add_argument('args', nargs=argparse.REMAINDER, help='arguments to pass to the task')
    args = parser.parse_args()
    exit_code = run(name=args.name, args=args.args, list=args.list, parser=parser)
    sys.exit(exit_code)


def run(
    name: str,
    args: List[str],
    list: bool = False,  # pylint: disable=redefined-builtin
    parser: Optional[argparse.ArgumentParser] = None,
) -> int:
    try:
        runner = TaskRunner(Path.cwd())

        if list:
            runner.list()
            return 0

        if name is None:
            raise InvalidUsageError(parser)

        return runner.run(name, args)
    except TaskipyError as e:
        print(e)
        return e.exit_code
    except Exception as e:
        print(e)
        return 1


if __name__ == '__main__':
    main()
