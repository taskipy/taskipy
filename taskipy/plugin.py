# pylint: disable=import-error

from pathlib import Path

from cleo.commands.command import Command
from cleo.exceptions import LogicException
from cleo.helpers import argument, option
from poetry.console.application import Application
from poetry.plugins.application_plugin import ApplicationPlugin

from taskipy.cli import run
from taskipy.task_runner import TaskRunner


class TaskipyCommand(Command):
    name = 'task'
    description = 'Taskipy - the complementary task runner for python.'
    options = [option('list', 'l', 'Show list of available tasks.')]
    arguments = [
        argument('name', 'Name of the task.', optional=True),
        argument(
            'args', 'Arguments to pass to the task.', optional=True, multiple=True
        ),
    ]

    def handle(self) -> int:
        name = self.argument('name')
        args = self.argument('args')
        return run(name=name, args=args, list=self.option('list'))


class BaseCommand(Command):
    description = 'A taskipy task'
    arguments = [
        argument(
            'args', 'Arguments to pass to the task.', optional=True, multiple=True
        ),
    ]
    hidden = True

    @classmethod
    def from_task(cls, task: str) -> 'BaseCommand':
        return type(f'{task.capitalize()}Class', (cls,), {'name': task})()

    def handle(self) -> int:
        return run(name=self.name, args=self.argument('args'))


class Plugin(ApplicationPlugin):
    def activate(self, application: Application) -> None:
        # Register `poetry task`
        application.command_loader.register_factory(
            TaskipyCommand.name,
            lambda: TaskipyCommand(),  # pylint: disable=unnecessary-lambda
        )
        # Register each `poetry <task>`
        runner = TaskRunner(Path.cwd())
        for task in runner.project.tasks:
            try:
                application.command_loader.register_factory(
                    task, lambda t=task: BaseCommand.from_task(t)
                )
            except LogicException:
                pass  # Attempted to register existing command
