import shutil
import textwrap
from typing import Iterable, Optional

import colorama  # type: ignore

from taskipy.exceptions import EmptyTasksSectionError
from taskipy.task import Task


class TasksListFormatter:
    def __init__(self, tasks: Iterable[Task]):
        if not tasks:
            raise EmptyTasksSectionError()

        self.__tasks = tasks
        colorama.init()

    def print(self, line_width: Optional[int] = None):
        if not line_width:
            line_width = shutil.get_terminal_size().columns

        tasks_col = [task.name for task in self.__tasks]
        longest_item_in_tasks_col = len(max(tasks_col, key=len))

        desc_col_wrap_indent = " " * (longest_item_in_tasks_col + 1)
        desc_col_width = line_width - len(desc_col_wrap_indent)

        for task in self.__tasks:
            name_text = task.name
            desc_text = task.description or task.command

            tasks_col_text = f"{name_text:<{longest_item_in_tasks_col}}"
            desc_col_text = "\n".join(
                textwrap.wrap(
                    desc_text,
                    width=desc_col_width,
                    subsequent_indent=desc_col_wrap_indent,
                )
            )
            print(f"{self.__highlight(tasks_col_text)} {desc_col_text}")

    def __highlight(self, text: str):
        return f"{colorama.Fore.CYAN}{text}{colorama.Style.RESET_ALL}"
