import os
import random
import signal
import subprocess
import time
import unittest
import warnings
from os import path
from typing import List, Optional, Tuple

from parameterized import parameterized  # type: ignore
import psutil  # type: ignore

from tests.utils.project import (
    GenerateProjectFromFixture,
    GenerateProjectWithPyProjectToml,
    TempProjectDir
)


class TaskipyTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp_dirs: List[TempProjectDir] = []

    def tearDown(self):
        for tmp_dir in self._tmp_dirs:
            tmp_dir.clean()

    def run_task(
        self,
        task: str,
        args: Optional[List[str]] = None,
        cwd=os.curdir,
    ) -> Tuple[int, str, str]:
        args = args or []
        proc = self.start_taskipy_process(task, args=args, cwd=cwd)
        stdout, stderr = proc.communicate()
        return proc.returncode, stdout.decode(), str(stderr)

    def start_taskipy_process(
        self,
        task: str,
        args: Optional[List[str]] = None,
        cwd=os.curdir,
    ) -> subprocess.Popen:
        executable_path = path.abspath('task')
        args = args or []
        return subprocess.Popen([executable_path, task] + args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)

    def create_test_dir_from_fixture(self, fixture_name: str):
        project_generator = GenerateProjectFromFixture(path.join('tests', 'fixtures', fixture_name))
        tmp_dir = TempProjectDir(project_generator)
        self._tmp_dirs.append(tmp_dir)
        return tmp_dir.path

    def create_test_dir_with_py_project_toml(self, py_project_toml: str):
        project_generator = GenerateProjectWithPyProjectToml(py_project_toml)
        tmp_dir = TempProjectDir(project_generator)
        self._tmp_dirs.append(tmp_dir)
        return tmp_dir.path

    # pylint: disable=invalid-name
    def assertSubstr(self, substr: str, full_string: str):
        self.assertTrue(substr in full_string, msg=f'Expected \n  "{substr}"\nto be in\n  "{full_string}"')

    # pylint: disable=invalid-name
    def assertNotSubstr(self, substr: str, full_string: str):
        self.assertFalse(substr in full_string, msg=f'Expected \n  "{substr}"\nnot to be in\n  "{full_string}"')

    # pylint: disable=invalid-name
    def assertSubstrsInOrder(self, substrs: List[str], full_string: str):
        self.assertGreater(len(substrs), 0, 'please provide at least one substr')

        for substr_a, substr_b in zip(substrs[:-1], substrs[1:]):
            self.assertSubstr(substr_a, full_string)
            self.assertSubstr(substr_b, full_string)
            self.assertLess(full_string.find(substr_a),
                            full_string.find(substr_b),
                            msg=f'Expected \n  "{substr_a}"\nto appear before\n  "{substr_b}"\nin\n  "{full_string}"')

    def assertTerminalTextEqual(self, expected: str, actual: str):
        expected_without_ansi_chars = expected.encode('ascii', 'ignore')
        actual_without_ansi_chars = actual.encode('ascii', 'ignore')
        self.assertEqual(expected_without_ansi_chars, actual_without_ansi_chars)


class RunTaskTestCase(TaskipyTestCase):
    def test_running_task(self):
        cwd = self.create_test_dir_from_fixture('project_with_pyproject_and_tasks')
        self.run_task('create_hello_txt', cwd=cwd)

        with open(path.join(cwd, 'hello.txt'), 'r', encoding='utf-8') as f:
            hello_file_contents = f.readline().strip()

        self.assertEqual(hello_file_contents, 'hello, world')

    def test_exit_code_matches_task_exit_code(self):
        cwd = self.create_test_dir_from_fixture('project_with_pyproject_and_tasks')
        exit_code, _, _ = self.run_task('exit_17', cwd=cwd)

        self.assertEqual(exit_code, 17)

    def test_stdout_contains_task_stdout(self):
        cwd = self.create_test_dir_from_fixture('project_with_pyproject_and_tasks')
        _, stdout, _ = self.run_task('print_hello_stdout', cwd=cwd)

        self.assertSubstr('hello stdout', stdout)

    def test_stderr_contains_task_stderr(self):
        cwd = self.create_test_dir_from_fixture('project_with_pyproject_and_tasks')
        _, _, stderr = self.run_task('print_hello_stderr', cwd=cwd)

        self.assertSubstr('hello stderr', stderr)


class TaskPrePostHooksTestCase(TaskipyTestCase):
    def test_running_pre_task_hook(self):
        cwd = self.create_test_dir_from_fixture('project_with_pre_post_task_hooks')
        _, stdout, _ = self.run_task('hello', cwd=cwd)

        self.assertSubstrsInOrder(['pre_task', 'hello'], stdout)

    def test_running_post_task_hook(self):
        cwd = self.create_test_dir_from_fixture('project_with_pre_post_task_hooks')
        _, stdout, _ = self.run_task('hello', cwd=cwd)

        self.assertSubstrsInOrder(['hello', 'post_task'], stdout)

    def test_exiting_after_pre_task_hook_if_exit_code_not_0(self):
        cwd = self.create_test_dir_from_fixture('project_with_pre_post_task_hooks')
        exit_code, stdout, _ = self.run_task('hello_failed_pretask', cwd=cwd)

        self.assertSubstr('pre_task', stdout)
        self.assertNotSubstr('hello', stdout)
        self.assertEqual(exit_code, 1)

    def test_exiting_with_post_task_hook_exit_code_if_not_0(self):
        cwd = self.create_test_dir_from_fixture('project_with_pre_post_task_hooks')
        exit_code, stdout, _ = self.run_task('hello_failed_posttask', cwd=cwd)

        self.assertSubstr('post_task', stdout)
        self.assertEqual(exit_code, 1)


class PassArgumentsTestCase(TaskipyTestCase):
    def test_running_task_with_positional_arguments(self):
        cwd = self.create_test_dir_from_fixture('project_with_tasks_that_accept_arguments')
        some_random_number = random.randint(1, 1000)
        exit_code, stdout, _ = self.run_task('echo_number', args=[f'{some_random_number}'], cwd=cwd)

        self.assertSubstr(f'the number is {some_random_number}', stdout)
        self.assertEqual(exit_code, 0)

    def test_running_task_with_named_arguments(self):
        cwd = self.create_test_dir_from_fixture('project_with_tasks_that_accept_arguments')
        exit_code, stdout, _ = self.run_task('echo_named', args=['-h'], cwd=cwd)

        self.assertSubstr('got a named argument -h', stdout)
        self.assertEqual(exit_code, 0)

    def test_running_task_with_multiple_arguments(self):
        cwd = self.create_test_dir_from_fixture('project_with_tasks_that_accept_arguments')
        args = ['one', 'two', 'three', 'four', 'five']
        exit_code, stdout, _ = self.run_task('echo_args_count', args=args, cwd=cwd)

        self.assertSubstr('the argument count is 5', stdout)
        self.assertEqual(exit_code, 0)

    def test_running_task_with_arguments_with_spaces(self):
        cwd = self.create_test_dir_from_fixture('project_with_task_that_checks_args_passed_with_spaces')
        name = 'Roy Sommer'
        age = random.randrange(1, 100)
        exit_code, stdout, _ = self.run_task('identify', args=['--full-name', name, '--age', f'{age}'], cwd=cwd)

        self.assertSubstr(f'name: {name} age: {age}', stdout)
        self.assertEqual(exit_code, 0)

    def test_running_task_arguments_not_passed_to_pre_hook(self):
        cwd = self.create_test_dir_from_fixture('project_with_tasks_that_accept_arguments')
        some_random_number = random.randint(1, 1000)
        exit_code, stdout, _ = self.run_task('echo_on_prehook', args=[f'{some_random_number}'], cwd=cwd)

        self.assertSubstr('the number in prehook is', stdout)
        self.assertNotSubstr(f'the number in prehook is {some_random_number}', stdout)
        self.assertEqual(exit_code, 0)

    def test_running_task_arguments_not_passed_to_post_hook(self):
        cwd = self.create_test_dir_from_fixture('project_with_tasks_that_accept_arguments')
        some_random_number = random.randint(1, 1000)
        exit_code, stdout, _ = self.run_task('echo_on_posthook', args=[f'{some_random_number}'], cwd=cwd)

        self.assertSubstr('the number in posthook is', stdout)
        self.assertNotSubstr(f'the number in posthook is {some_random_number}', stdout)
        self.assertEqual(exit_code, 0)


class ListTasksTestCase(TaskipyTestCase):
    project_tasks_output = "\n".join([
        "one   echo first task",
        "two   echo second task",
        "three echo third task",
    ])

    def test_running_task_list(self):
        cwd = self.create_test_dir_from_fixture('project_with_tasks_to_list')
        exit_code, stdout, _ = self.run_task('--list', cwd=cwd)

        self.assertTerminalTextEqual(self.project_tasks_output, stdout.strip())
        self.assertEqual(exit_code, 0)

    def test_running_task_list_with_shorthand(self):
        cwd = self.create_test_dir_from_fixture('project_with_tasks_to_list')
        exit_code, stdout, _ = self.run_task('-l', cwd=cwd)

        self.assertTerminalTextEqual(self.project_tasks_output, stdout.strip())
        self.assertEqual(exit_code, 0)

    def test_running_task_list_before_name(self):
        cwd = self.create_test_dir_from_fixture('project_with_tasks_to_list')
        # anything following the flag should be ignored
        exit_code, stdout, _ = self.run_task('--list', ['one'], cwd=cwd)

        self.assertTerminalTextEqual(self.project_tasks_output, stdout.strip())
        self.assertEqual(exit_code, 0)

    def test_running_task_list_with_arg(self):
        cwd = self.create_test_dir_from_fixture('project_with_tasks_to_list')
        # when --list follows after task name it should be passed as an argument
        exit_code, stdout, _ = self.run_task('one', ['--list'], cwd=cwd)
        expected = "first task --list"

        self.assertTerminalTextEqual(expected, stdout.strip())
        self.assertEqual(exit_code, 0)

    def test_running_task_list_no_tasks(self):
        py_project_toml = '''
            [tool.taskipy.tasks]
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('--list', cwd=cwd)

        self.assertTerminalTextEqual('no tasks found. create your first task by adding it to your pyproject.toml file under [tool.taskipy.tasks]', stdout.strip())
        self.assertEqual(exit_code, 127)

    def test_running_task_list_no_tasks_section(self):
        py_project_toml = ''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('--list', cwd=cwd)

        self.assertTerminalTextEqual('no tasks found. add a [tool.taskipy.tasks] section to your pyproject.toml', stdout.strip())
        self.assertEqual(exit_code, 127)


class TaskDescriptionTestCase(TaskipyTestCase):
    def test_running_task_with_description(self):
        py_project_toml = '''
            [tool.taskipy.tasks]
            print_age = { cmd = "echo age is 29", help = "prints the age" }
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        _, stdout, _ = self.run_task('print_age', cwd=cwd)

        self.assertSubstr('age is 29', stdout)

    def test_listing_task_with_description(self):
        py_project_toml = '''
            [tool.taskipy.tasks]
            print_age = { cmd = "echo age is 29", help = "prints the age" }
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        _, stdout, _ = self.run_task('--list', cwd=cwd)

        self.assertSubstr('prints the age', stdout)

    def test_reject_task_for_not_having_cmd(self):
        py_project_toml = '''
            [tool.taskipy.tasks]
            print_age = { help = "prints the age" }
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('print_age', cwd=cwd)

        self.assertEqual(exit_code, 1)
        self.assertSubstr('the task item does not have the "cmd" property', stdout)

    def test_allow_task_to_not_have_help(self):
        py_project_toml = '''
            [tool.taskipy.tasks]
            print_age = { cmd = "echo age is 29" }
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('print_age', cwd=cwd)

        self.assertEqual(exit_code, 0)
        self.assertSubstr('age is 29', stdout)

    def test_reject_task_that_is_not_string_nor_object(self):
        py_project_toml = '''
            [tool.taskipy.tasks]
            print_age = 5
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('print_age', cwd=cwd)

        self.assertEqual(exit_code, 1)
        self.assertSubstr('tasks must be strings, or dicts that contain { cmd, help, use_vars }', stdout)


class TaskRunFailTestCase(TaskipyTestCase):
    def test_exiting_with_code_127_and_printing_if_task_not_found(self):
        cwd = self.create_test_dir_from_fixture('project_with_pyproject_and_tasks')
        exit_code, stdout, _ = self.run_task('task_that_does_not_exist', cwd=cwd)

        self.assertSubstr('could not find task "task_that_does_not_exist"', stdout)
        self.assertEqual(exit_code, 127)

    def test_exiting_with_code_127_and_printing_if_no_arg_is_passed(self):
        cwd = self.create_test_dir_from_fixture('project_with_pyproject_and_tasks')
        executable_path = path.abspath('task')
        proc = subprocess.Popen(
            executable_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd
        )
        stdout, _ = proc.communicate()

        self.assertSubstr('usage: task', stdout.decode())
        self.assertEqual(proc.returncode, 127)

    def test_exiting_with_code_127_and_printing_if_no_tasks_section(self):
        cwd = self.create_test_dir_from_fixture('project_with_pyproject_without_tasks_section')
        exit_code, stdout, _ = self.run_task('task_that_does_not_exist', cwd=cwd)

        self.assertSubstr('no tasks found. add a [tool.taskipy.tasks] section to your pyproject.toml', stdout)
        self.assertEqual(exit_code, 127)

    def test_exiting_with_code_1_and_printing_if_no_pyproject_toml_file_found(self):
        cwd = self.create_test_dir_from_fixture('project_without_pyproject')
        exit_code, stdout, _ = self.run_task('some_task', cwd=cwd)

        self.assertSubstr('no pyproject.toml file found in this directory or parent directories', stdout)
        self.assertEqual(exit_code, 1)

    def test_exiting_with_code_1_and_printing_if_pyproject_toml_file_is_malformed(self):
        cwd = self.create_test_dir_from_fixture('project_with_malformed_pyproject')
        exit_code, stdout, _ = self.run_task('some_task', cwd=cwd)

        self.assertSubstr('pyproject.toml file is malformed and could not be read', stdout)
        self.assertEqual(exit_code, 1)


class InterruptingTaskTestCase(TaskipyTestCase):
    def setUp(self):
        super().setUp()

        # suppress resource warnings, as they are false positives caused by psutil
        warnings.simplefilter('ignore', category=ResourceWarning)

    def interrupt_task(self, process: subprocess.Popen):
        psutil_process_wrapper = psutil.Process(process.pid)

        processes = psutil_process_wrapper.children(recursive=True)

        innermost_process = next(filter(lambda p: p.name().lower().startswith('python'), processes))
        innermost_process.send_signal(signal.SIGINT)

    def test_handling_sigint_according_to_subprocess_if_it_handles_it_gracefully(self):
        cwd = self.create_test_dir_from_fixture('project_with_tasks_that_handle_interrupts')
        process = self.start_taskipy_process('run_loop_with_interrupt_handling', cwd=cwd)

        time.sleep(.2)

        self.interrupt_task(process)
        exit_code = process.wait()

        self.assertEqual(exit_code, 0)

    def test_handling_sigint_according_to_subprocess_if_it_does_not_handle_it_gracefully(self):
        cwd = self.create_test_dir_from_fixture('project_with_tasks_that_handle_interrupts')
        process = self.start_taskipy_process('run_loop_without_interrupt_handling', cwd=cwd)

        time.sleep(.2)

        self.interrupt_task(process)

        exit_code = process.wait()

        self.assertEqual(exit_code, 130)

    def test_sigterm_should_be_sent_to_subprocess(self):
        cwd = self.create_test_dir_from_fixture('project_with_tasks_that_handle_sigterm')
        process = self.start_taskipy_process('run_loop_with_sigterm_handling', cwd=cwd)

        time.sleep(.2)

        process.send_signal(signal.SIGTERM)

        exit_code = process.wait()
        stdout, _ = process.communicate()

        self.assertEqual(exit_code, 123)
        self.assertSubstr('sigterm', str(stdout))


class CustomRunnerTestCase(TaskipyTestCase):
    def test_running_command_with_custom_runner(self):
        py_project_toml = '''
            [tool.taskipy.settings]
            runner = "time"

            [tool.taskipy.tasks]
            print_with_python = "python -c 'print(1337)'"
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        _, _, stderr = self.run_task('print_with_python', cwd=cwd)

        time_cmd_output_format = 'user'
        self.assertSubstr(time_cmd_output_format, stderr)

    def test_running_command_with_custom_runner_with_trailing_space(self):
        py_project_toml = '''
            [tool.taskipy.settings]
            runner = "time "

            [tool.taskipy.tasks]
            print_with_python = "python -c 'print(1337)'"
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        _, _, stderr = self.run_task('print_with_python', cwd=cwd)

        time_cmd_output_format = 'user'
        self.assertSubstr(time_cmd_output_format, stderr)

    def test_running_command_with_custom_runner_fails_if_custom_runner_is_not_string(self):
        py_project_toml = '''
            [tool.taskipy.settings]
            runner = 55

            [tool.taskipy.tasks]
            print_with_python = "python -c 'print(1337)'"
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('print_with_python', cwd=cwd)

        self.assertSubstr('invalid value: runner is not a string. please check [tool.taskipy.settings.runner]', stdout)
        self.assertEqual(exit_code, 1)


class TaskFromChildTestCase(TaskipyTestCase):
    def test_running_parent_pyproject_task_from_child_directory(self):
        cwd = self.create_test_dir_from_fixture('project_with_tasks_from_child')
        _, stdout, _ = self.run_task('print_current_dir_name', cwd=path.join(cwd, 'child_without_pyproject'))

        self.assertSubstr('child_without_pyproject', stdout)

    def test_find_nearest_pyproject_from_child_directory(self):
        cwd = self.create_test_dir_from_fixture('project_with_tasks_from_child')
        _, stdout, _ = self.run_task('hello', cwd=path.join(cwd, 'child_with_pyproject'))

        self.assertSubstr('hello from child', stdout)


class UseVarsTestCase(TaskipyTestCase):
    def test_use_vars_working(self):
        py_project_toml = '''
            [tool.taskipy.variables]
            name = "John Doe"

            [tool.taskipy.tasks]
            echo = { cmd = "echo hello {name:<10}:", use_vars = true }
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('echo', cwd=cwd)
        self.assertSubstr('hello John Doe :', stdout)
        self.assertEqual(exit_code, 0)

    def test_use_vars_no_param(self):
        py_project_toml = '''
            [tool.taskipy.variables]
            name = "John Doe"

            [tool.taskipy.tasks]
            echo = { cmd = "echo hello {name}" }
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('echo', cwd=cwd)
        self.assertSubstr('hello {name}', stdout)
        self.assertEqual(exit_code, 0)

    def test_use_vars_param_disabled(self):
        py_project_toml = '''
            [tool.taskipy.variables]
            name = "John Doe"

            [tool.taskipy.tasks]
            echo = { cmd = "echo hello {name}", use_vars = false }
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('echo', cwd=cwd)
        self.assertSubstr('hello {name}', stdout)
        self.assertEqual(exit_code, 0)

    def test_use_vars_str_task_no_param(self):
        py_project_toml = '''
            [tool.taskipy.variables]
            name = "John Doe"

            [tool.taskipy.tasks]
            echo = "echo hello {name}"
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('echo', cwd=cwd)
        self.assertSubstr('hello {name}', stdout)
        self.assertEqual(exit_code, 0)

    def test_use_vars_param_malformed(self):
        py_project_toml = '''
            [tool.taskipy.variables]
            name = "John Doe"

            [tool.taskipy.tasks]
            echo = { cmd = "echo hello {name}", use_vars = 1 }
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('echo', cwd=cwd)
        self.assertSubstr('task\'s "use_vars" arg has to be bool', stdout)
        self.assertEqual(exit_code, 1)

    def test_use_vars_missing_var(self):
        py_project_toml = '''
            [tool.taskipy.tasks]
            echo = { cmd = "echo hello {name}", use_vars = true }
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('echo', cwd=cwd)
        self.assertSubstr("reason: 'name' variable expected in [tool.taskipy.variables]", stdout)
        self.assertEqual(exit_code, 1)

    def test_use_vars_setting(self):
        py_project_toml = '''
            [tool.taskipy.settings]
            use_vars = true

            [tool.taskipy.variables]
            name = "John Doe"

            [tool.taskipy.tasks]
            echo = "echo hello {name:<10}:"
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('echo', cwd=cwd)
        self.assertSubstr('hello John Doe :', stdout)
        self.assertEqual(exit_code, 0)

    def test_use_vars_setting_override_to_false(self):
        py_project_toml = '''
            [tool.taskipy.settings]
            use_vars = true

            [tool.taskipy.variables]
            name = "John Doe"

            [tool.taskipy.tasks]
            echo = { cmd = "echo hello {name}:", use_vars = false }
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('echo', cwd=cwd)
        self.assertSubstr('hello {name}:', stdout)
        self.assertEqual(exit_code, 0)

    def test_use_vars_setting_override_to_true(self):
        py_project_toml = '''
            [tool.taskipy.settings]
            use_vars = false

            [tool.taskipy.variables]
            name = "John Doe"

            [tool.taskipy.tasks]
            echo = { cmd = "echo hello {name}:", use_vars = true }
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('echo', cwd=cwd)
        self.assertSubstr('hello John Doe:', stdout)
        self.assertEqual(exit_code, 0)


class RecursiveVariablesTestCase(TaskipyTestCase):
    def test_recursive_variables_can_use_other_variables(self):
        py_project_toml = '''
            [tool.taskipy.settings]
            use_vars = true

            [tool.taskipy.variables]
            first_name = "John"
            last_name = "Doe"
            full_name = { var = "{first_name} {last_name}", recursive = true }

            [tool.taskipy.tasks]
            echo = "echo hello {full_name}"
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('echo', cwd=cwd)
        self.assertSubstr('hello John Doe', stdout)
        self.assertEqual(exit_code, 0)

    def test_recursive_variables_can_use_other_recursive_variables(self):
        py_project_toml = '''
            [tool.taskipy.settings]
            use_vars = true

            [tool.taskipy.variables]
            first_name = "John"
            last_name = "Doe"
            full_name = { var = "{first_name} {last_name}", recursive = true }
            another_name = { var = "{full_name} another name!", recursive = true }
            even_another_name = { var = "{another_name} {full_name}", recursive = true }

            [tool.taskipy.tasks]
            echo = "echo hello {even_another_name}"
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('echo', cwd=cwd)
        self.assertSubstr('hello John Doe another name! John Doe', stdout)
        self.assertEqual(exit_code, 0)

    def test_error_is_raised_if_a_cycle_is_detected(self):
        py_project_toml = '''
            [tool.taskipy.settings]
            use_vars = true

            [tool.taskipy.variables]
            last_name = { var = "{first_name}", recursive = true }
            first_name = { var = "{last_name}", recursive = true }

            [tool.taskipy.tasks]
            echo = "echo hello {first_name} {last_name}!"
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('echo', cwd=cwd)
        self.assertSubstr('cannot resolve variables, found variables that depend on each other', stdout)
        self.assertEqual(exit_code, 127)

    def test_non_recursive_variables_cant_use_other_variables(self):
        py_project_toml = '''
            [tool.taskipy.settings]
            use_vars = true

            [tool.taskipy.variables]
            first_name = "John"
            last_name = "Doe"
            full_name_1 = "{first_name} {last_name}"
            full_name_2 = { var = "{first_name} {last_name}", recursive = false }

            [tool.taskipy.tasks]
            echo = "echo full_name_1: {full_name_1} full_name_2: {full_name_2}!"
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('echo', cwd=cwd)
        self.assertSubstr('full_name_1: {first_name} {last_name} full_name_2: {first_name} {last_name}', stdout)
        self.assertEqual(exit_code, 0)


class VariableSchemaTestCase(TaskipyTestCase):
    def test_variables_can_be_strings(self):
        py_project_toml = '''
            [tool.taskipy.variables]
            name = "John"

            [tool.taskipy.tasks]
            echo = { cmd = "echo {name}", use_vars = true }
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('echo', cwd=cwd)
        self.assertSubstr('John', stdout)
        self.assertEqual(exit_code, 0)

    def test_variables_can_be_a_table_with_var_key_and_no_recursive_key(self):
        py_project_toml = '''
            [tool.taskipy.variables]
            name = { var = "John" }

            [tool.taskipy.tasks]
            echo = { cmd = "echo {name}", use_vars = true }
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('echo', cwd=cwd)
        self.assertSubstr('John', stdout)
        self.assertEqual(exit_code, 0)

    def test_variables_can_be_a_table_with_var_key_and_recursive_key(self):
        py_project_toml = '''
            [tool.taskipy.variables]
            name = { var = "John", recursive = true }

            [tool.taskipy.tasks]
            echo = { cmd = "echo {name}", use_vars = true }
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('echo', cwd=cwd)
        self.assertSubstr('John', stdout)
        self.assertEqual(exit_code, 0)

    def test_variable_table_by_default_is_not_recursive(self):
        py_project_toml = '''
            [tool.taskipy.variables]
            test = "test var"
            name = { var = "{test}" }

            [tool.taskipy.tasks]
            echo = { cmd = "echo {name}", use_vars = true }
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('echo', cwd=cwd)
        self.assertSubstr('{test}', stdout)
        self.assertEqual(exit_code, 0)

    def test_regular_string_variable_are_not_recursive(self):
        py_project_toml = '''
            [tool.taskipy.variables]
            test = "test var"
            name = "{test}"

            [tool.taskipy.tasks]
            echo = { cmd = "echo {name}", use_vars = true }
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('echo', cwd=cwd)
        self.assertSubstr('{test}', stdout)
        self.assertEqual(exit_code, 0)

    @parameterized.expand([(5,), (5.5, ), ([], ), ("false",), ({},)])
    def test_other_variable_schemas_are_rejected_with_invalid_variable_error(
        self, value
    ):
        py_project_toml = f'''
            [tool.taskipy.variables]
            test = {value}
        ''' + '''
            [tool.taskipy.tasks]
            echo = { cmd = "echo {test}", use_vars = true }
        '''
        cwd = self.create_test_dir_with_py_project_toml(py_project_toml)
        exit_code, stdout, _ = self.run_task('echo', cwd=cwd)
        self.assertSubstr('variable test is invalid', stdout)
        self.assertEqual(exit_code, 127)
