#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from typing import List, Union

from taskipy.exceptions import InvalidUsageError, TaskipyError
from taskipy.task_runner import TaskRunner


def main():
    exit_code = run(sys.argv[1:])
    sys.exit(exit_code)


def run(args: List[str], cwd: Union[str, Path, None] = None) -> int:
    """Run the taskipy CLI programmatically.

    Args:
        args: The arguments passed to the taskipy CLI.
        cwd: The working directory to run the task in. If not
            provided, defaults to the current working directory.

    Returns:
        0 on success; > 0 for an error.
    """
    parser = argparse.ArgumentParser(
        prog="task",
        description=(
            "runs a task specified in your pyproject.toml " "under [tool.taskipy.tasks]"
        ),
    )
    parser.add_argument(
        "-l", "--list", help="show list of available tasks", action="store_true"
    )
    parser.add_argument("name", help="name of the task", nargs="?")
    parser.add_argument(
        "args", nargs=argparse.REMAINDER, help="arguments to pass to the task"
    )
    parsed_args = parser.parse_args(args=args)

    try:
        cwd = Path(cwd).resolve() if cwd is not None else Path.cwd()
        runner = TaskRunner(cwd)

        if parsed_args.list:
            runner.list()
            return 0

        if parsed_args.name is None:
            raise InvalidUsageError(parser)

        return runner.run(parsed_args.name, parsed_args.args)
    except TaskipyError as e:
        print(e, file=sys.stderr)
        return e.exit_code
    except Exception as e:
        print(e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    main()
