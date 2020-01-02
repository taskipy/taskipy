#!/usr/bin/env python3
import argparse
from taskipy.run import run_task

def main():
    parser = argparse.ArgumentParser(prog='task', description='runs a task specified in your pyproject.toml under [tool.taskipy.tasks]')
    parser.add_argument('name', help='name of the task')
    parser.add_argument('args', nargs=argparse.REMAINDER, help='arguments to pass to the task')
    args = parser.parse_args()

    run_task(args.name, args.args)

if __name__ == '__main__':
    main()
