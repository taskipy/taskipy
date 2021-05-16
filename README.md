<p align="center">
<img src="./logo.svg" width="150" />
</p>

<p align="center">

[![pypi](https://img.shields.io/pypi/v/taskipy?style=flat-square)](https://pypi.org/project/taskipy/)
[![ci](https://img.shields.io/github/workflow/status/illberoy/taskipy/Taskipy%20Test%20CI?style=flat-square)](https://github.com/illBeRoy/taskipy/actions?query=workflow%3A%22Taskipy+Test+CI%22)
[![All Contributors](https://img.shields.io/github/all-contributors/illberoy/taskipy?color=orange&style=flat-square)](#contributors-)

</p>


## General
**> The complementary task runner for python. _**

Every development pipeline has tasks, such as `test`, `lint` or `publish`. With taskipy, you can define those tasks in one file and run them with a simple command.

For instance, instead of running the following command:
```bash
python -m unittest tests/test_*.py
```

You can create a task called `test` and simply run:
```bash
poetry run task test
```

Or (if you're not using poetry):
```bash
task test
```

In addition, you can compose tasks and group them together, and also create dependencies between them.

This project is heavily inspired by npm's [run script command](https://docs.npmjs.com/cli/run-script).

## Requirements
Python 3.6 or newer.

Your project directory should include a valid `pyproject.toml` file, as specified in [PEP-518](https://www.python.org/dev/peps/pep-0518/).

## Usage
### Installation
To install taskipy as a dev dependency, simply run:
```bash
poetry add --dev taskipy
```

### Adding Tasks 
In your `pyproject.toml` file, add a new section called `[tool.taskipy.tasks]`.

The section is a key-value map, from the names of the task to the actual command that should be run in the shell.

There are two ways to define tasks. The easy way is to simply write the command down as a string:

__pyproject.toml__
```toml
[tool.taskipy.tasks]
test = "python -m unittest tests/test_*.py"
lint = "pylint tests taskipy"
```

Alternatively, you can define tasks more explicitly by declaring both the command and a helpful description using an inline table:

__pyproject.toml__
```toml
[tool.taskipy.tasks]
test = { cmd = "python -m unittest tests/test_*.py", help = "runs all unit tests" }
lint = { cmd = "pylint tests taskipy", help = "confirms code style using pylint" } 
```

The explicit notation is more verbose, but provides better context to anyone who uses the task.

### Running Tasks
In order to run a task, run the following command in your terminal:
```bash
$ poetry run task test
```

You can also list all existing tasks by running the following:
```bash
$ poetry run task --list
test                python -m unittest tests/test_*.py
lint                pylint tests taskipy
```

If you declared your task explicitly, you will see the description of the task by the side of the task's name:
```bash
$ poetry run task --list
test                runs all unit tests
lint                confirms code style using pylint
```

### Passing Command Line Args to Tasks
If you want to pass command line arguments to tasks (positional or named), simply append them to the end of the task command.

For example, running the above task like this:
```bash
poetry run task test -h
```

Is equivalent to running:
```bash
python -m unittest tests/test_*.py -h
```

And will show unittest's help instead of actually running it.

> ⚠️ Note: if you are using pre \ post hooks, do notice that arguments are not passed to them, only to the task itself.

### Composing Tasks
#### Grouping Subtasks Together
Some tasks are composed of multiple subtasks. Instead of writing plain shell commands and stringing them together, you can break them down into multiple subtasks:
```toml
[tool.taskipy.tasks]
lint_pylint = "pylint tests taskipy"
lint_mypy = "mypy tests taskipy"
```

And then create a composite task:
```toml
[tool.taskipy.tasks]
lint = "task lint_pylint && task lint_mypy"
lint_pylint = "pylint tests taskipy"
lint_mypy = "mypy tests taskipy"
```

#### Pre Task Hook
Tasks might also depend on one another. For example, tests might require some binaries to be built. Take the two following commands, for instance:
```toml
[tool.taskipy.tasks]
test = "python -m unittest tests/test_*.py"
build = "make ."
```

You could make tests depend on building, by using the **pretask hook**:
```toml
[tool.taskipy.tasks]
pre_test = "task build"
test = "python -m unittest tests/test_*.py"
build = "make ."
```

The pretask hook looks for `pre_<task_name>` task for a given `task_name`. It will run it before running the task itself. If the pretask fails, then taskipy will exit without running the task itself.

#### Post Task Hook
From time to time, you might want to run a task in conjuction with another. For example, you might want to run linting after a successful test run. Take the two following commands, for instance:
```toml
[tool.taskipy.tasks]
test = "python -m unittest tests/test_*.py"
lint = "pylint tests taskipy"
```

You could make tests trigger linting, by using the **posttask hook**:
```toml
[tool.taskipy.tasks]
test = "python -m unittest tests/test_*.py"
post_test = "task lint"
lint = "pylint tests taskipy"
```

The posttask hook looks for `post_<task_name>` task for a given `task_name`. It will run it after running the task itself. If the task failed, then taskipy will not run the posttask hook.

### Using Taskipy Without Poetry
Taskipy was created with poetry projects in mind, but actually only requires a valid `pyproject.toml` file in your project's directory. As a result, you can use it even eithout poetry:

#### Installing With PIP
Install taskipy on your machine or in your virtualenv using:
```bash
pip install taskipy
```

#### Running Tasks
Head into your project's directory (don't forget to activate virtualenv if you're using one), and run the following command:
```bash
task TASK
```
Where `TASK` is the name of your task.

### Advanced Use Cases
If you have a more specific use case, you might not be the first to run into it! Head over to the [ADVANCED_FEATURES](./docs/ADVANCED_FEATURES.md) doc, and look it up.

## Maintainers 🚧

<table>
  <tr>
    <td align="center"><a href="https://github.com/illBeRoy"><img src="https://avatars2.githubusercontent.com/u/6681893?v=4" width="100px;" alt=""/><br /><sub><b>Roy Sommer</b></sub></a></td>
  </tr>
</table>

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="http://triguba.com"><img src="https://avatars3.githubusercontent.com/u/15860938?v=4" width="100px;" alt=""/><br /><sub><b>Eugene Triguba</b></sub></a><br /><a href="https://github.com/illBeRoy/taskipy/commits?author=eugenetriguba" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/RobinFrcd"><img src="https://avatars0.githubusercontent.com/u/29704178?v=4" width="100px;" alt=""/><br /><sub><b>RobinFrcd</b></sub></a><br /><a href="https://github.com/illBeRoy/taskipy/commits?author=RobinFrcd" title="Code">💻</a></td>
    <td align="center"><a href="http://granitosaurus.rocks"><img src="https://avatars0.githubusercontent.com/u/5476164?v=4" width="100px;" alt=""/><br /><sub><b>Bernardas Ališauskas</b></sub></a><br /><a href="https://github.com/illBeRoy/taskipy/commits?author=Granitosaurus" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
