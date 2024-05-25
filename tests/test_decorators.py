import unittest
from io import StringIO
import sys
import time
from functools import wraps

from taskipy.decorators import apply_decorators, measure_time


def dummy_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Dummy decorator applied")
        return func(*args, **kwargs)

    return wrapper


def another_dummy_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Another dummy decorator applied")
        return func(*args, **kwargs)

    return wrapper


@measure_time
def sample_task(task_name):
    time.sleep(1)
    return f"Task {task_name} completed"


class TestDecorators(unittest.TestCase):

    def test_apply_decorators(self):
        decorators = [dummy_decorator, another_dummy_decorator]
        decorated_func = apply_decorators(sample_task, decorators)

        captured_output = StringIO()
        sys.stdout = captured_output

        result = decorated_func("Test Task")

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("Dummy decorator applied", output)
        self.assertIn("Another dummy decorator applied", output)
        self.assertIn("-- ran Test Task in 1.00s --", output)
        self.assertEqual(result, "Task Test Task completed")
