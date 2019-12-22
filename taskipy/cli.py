#!/usr/bin/env python3
import argparse
from taskipy.run import run_task

def main():
    parser = argparse.ArgumentParser(prog='task', description='runs a task specified in your pyproject.toml under [tool.taskify.tasks]')
    parser.add_argument('name', help='name of the task')
    args = parser.parse_args()

    run_task(args.name)

if __name__ == '__main__':
    main()
