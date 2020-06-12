#!/usr/bin/env python3
import argparse
import sys

from taskipy.exceptions import (
    InvalidRunnerTypeError,
    MalformedPyProjectError,
    MissingPyProjectFileError,
    MissingTaskipyTasksSectionError,
    TaskNotFoundError,
)
from taskipy.task_runner import TaskRunner


def main():
    parser = argparse.ArgumentParser(
        prog="task",
        description="runs a task specified in your pyproject.toml under [tool.taskipy.tasks]",
    )
    parser.add_argument("name", help="name of the task")
    parser.add_argument(
        "args", nargs=argparse.REMAINDER, help="arguments to pass to the task"
    )
    args = parser.parse_args()

    try:
        exit_code = TaskRunner(args.name, args.args).run()
        sys.exit(exit_code)
    except (TaskNotFoundError, MissingTaskipyTasksSectionError) as e:
        print(e)
        sys.exit(127)
    except (InvalidRunnerTypeError, MalformedPyProjectError, MissingPyProjectFileError) as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
