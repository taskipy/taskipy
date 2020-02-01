import os
import unittest
import subprocess
import random
import time
import signal
import psutil # type: ignore
import warnings
from os import path
from typing import List, Tuple
from tests.utils.fixture import FixtureTempDir

class TaskipyTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp_dirs: List[FixtureTempDir] = []

    def tearDown(self):
        for tmp_dir in self._tmp_dirs:
            tmp_dir.clean()

    def run_task(self, task: str, args: List[str] = None, cwd=os.curdir) -> Tuple[int, str, str]:
        proc = self.start_taskipy_process(task, args=args, cwd=cwd)
        stdout, stderr = proc.communicate()

        return proc.returncode, str(stdout), str(stderr)

    def start_taskipy_process(self, task: str, args: List[str] = None, cwd=os.curdir) -> subprocess.Popen:
        executable_path = path.abspath('task')
        args = args or []

        return subprocess.Popen([executable_path, task] + args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)

    def create_test_dir_from_fixture(self, fixture_name: str):
        tmp_dir = FixtureTempDir(path.join('tests', 'fixtures', fixture_name))
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

class RunTaskTestCase(TaskipyTestCase):
    def test_running_task(self):
        cwd = self.create_test_dir_from_fixture('project_with_pyproject_and_tasks')
        self.run_task('create_hello_txt', cwd=cwd)

        with open(path.join(cwd, 'hello.txt'), 'r') as f:
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

        self.assertSubstr(f'got a named argument -h', stdout)
        self.assertEqual(exit_code, 0)

    def test_running_task_with_multiple_arguments(self):
        cwd = self.create_test_dir_from_fixture('project_with_tasks_that_accept_arguments')
        args = ['one', 'two', 'three', 'four', 'five']
        exit_code, stdout, _ = self.run_task('echo_args_count', args=args, cwd=cwd)

        self.assertSubstr(f'the argument count is 5', stdout)
        self.assertEqual(exit_code, 0)

    def test_running_task_arguments_not_passed_to_pre_hook(self):
        cwd = self.create_test_dir_from_fixture('project_with_tasks_that_accept_arguments')
        some_random_number = random.randint(1, 1000)
        exit_code, stdout, _ = self.run_task('echo_on_prehook', args=[f'{some_random_number}'], cwd=cwd)

        self.assertSubstr(f'the number in prehook is', stdout)
        self.assertNotSubstr(f'the number in prehook is {some_random_number}', stdout)
        self.assertEqual(exit_code, 0)

    def test_running_task_arguments_not_passed_to_post_hook(self):
        cwd = self.create_test_dir_from_fixture('project_with_tasks_that_accept_arguments')
        some_random_number = random.randint(1, 1000)
        exit_code, stdout, _ = self.run_task('echo_on_posthook', args=[f'{some_random_number}'], cwd=cwd)

        self.assertSubstr(f'the number in posthook is', stdout)
        self.assertNotSubstr(f'the number in posthook is {some_random_number}', stdout)
        self.assertEqual(exit_code, 0)

class TaskRunFailTestCase(TaskipyTestCase):
    def test_exiting_with_code_127_and_printing_if_task_not_found(self):
        cwd = self.create_test_dir_from_fixture('project_with_pyproject_and_tasks')
        exit_code, stdout, _ = self.run_task('task_that_does_not_exist', cwd=cwd)

        self.assertSubstr('could not find task "task_that_does_not_exist"', stdout)
        self.assertEqual(exit_code, 127)

    def test_exiting_with_code_127_and_printing_if_no_tasks_section(self):
        cwd = self.create_test_dir_from_fixture('project_with_pyproject_without_tasks_section')
        exit_code, stdout, _ = self.run_task('task_that_does_not_exist', cwd=cwd)

        self.assertSubstr('no tasks found. add a [tool.taskipy.tasks] section to your pyproject.toml', stdout)
        self.assertEqual(exit_code, 127)

    def test_exiting_with_code_1_and_printing_if_no_pyproject_toml_file_found(self):
        cwd = self.create_test_dir_from_fixture('project_without_pyproject')
        exit_code, stdout, _ = self.run_task('some_task', cwd=cwd)

        self.assertSubstr('no pyproject.toml file found in this directory', stdout)
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

        innermost_process = next(filter(lambda p: p.name().startswith('python'), processes))
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
