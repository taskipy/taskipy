# Advanced Use Cases
This is a list of quality of life features that might be useful to you if you have a specific use case that you want to easily solve.

You can go over the use cases list and try to find the specific use case which you're trying to solve. If you cannot find your specific use case, feel free to open an issue or a PR!

## Use Cases
For each of the use cases below, click on the arrow in order to get to the relevant feature.
1. I want to load environment variables before every task ([⏩](#custom-runners))
2. I want to run all tasks in a specific virtualenv ([⏩](#custom-runners))
3. I want to run all tasks in a specific shell \ ssh ([⏩](#custom-runners))

## Features
### Custom Runners
#### Requirement
Under some circumstances, we would like to run all of our tasks in a consistent context; e.g., in a specific shell, a remote shell with `ssh`, some custom `virtualenv` wrapper, or even `dotenv`.

Currently, we can configure this on a task to task basis, e.g.:
```toml
[tool.taskipy.tasks]
test = "dotenv run unittest ."
```

But if we want all of our tasks to use the same runner (such as `dotenv` in the above example) we would have to manually write all of them as such:
```toml
[tool.taskipy.settings]
runner = "dotenv run"

[tool.taskipy.tasks]
test = "dotenv run unittest ."
lint = "dotenv run pylint taskipy"
release = "dotenv run release-it"
start = "dotenv run python ."
...
```

And so on.

Such cases are where we need a global wrapper, so we wouldn't have to repeat the prefix with every command.

#### Solution
The `tool.taskipy.settings.runner` option: when configured, adds the given runner command as a prefix to every task we run.

Let's take a look at the following example, where we want to load environment variables before every task:
```toml
[tool.taskipy.settings]
runner = "dotenv run"

[tool.taskipy.tasks]
test = "unittest ."
lint = "pylint taskipy"
```

Now, running `task test` will actually run:
```bash
dotenv run unittest .
```

Which means that we implicitly initialize the env before every task.
