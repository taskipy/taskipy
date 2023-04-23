import shutil
import textwrap
import colorama  # type: ignore
from typing import List, Type, Optional

from taskipy.io import AbstractIO
from taskipy.task import Task
from taskipy.exceptions import EmptyTasksSectionError


class TasksListFormatter:
    def __init__(self, tasks: List[Task]):
        if not tasks:
            raise EmptyTasksSectionError()

        self.__tasks = tasks
        colorama.init()

    def print(self, io: Type[AbstractIO], line_width: Optional[int] = None):  # pylint: disable=C0103
        if not line_width:
            line_width = shutil.get_terminal_size().columns

        tasks_col = [task.name for task in self.__tasks]
        longest_item_in_tasks_col = len(max(tasks_col, key=len))

        desc_col_wrap_indent = ' ' * (longest_item_in_tasks_col + 1)
        desc_col_width = line_width - len(desc_col_wrap_indent)

        for task in self.__tasks:
            name_text = task.name
            desc_text = task.description or task.command

            tasks_col_text = f'{name_text:<{longest_item_in_tasks_col}}'
            desc_col_text = '\n'.join(textwrap.wrap(desc_text,
                                                    width=desc_col_width,
                                                    subsequent_indent=desc_col_wrap_indent))
            io.write_line(f'{self.__highlight(tasks_col_text)} {desc_col_text}')

    def __highlight(self, text: str):
        return f'{colorama.Fore.CYAN}{text}{colorama.Style.RESET_ALL}'
