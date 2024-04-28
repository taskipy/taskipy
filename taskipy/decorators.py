from functools import wraps
import time
from typing import Callable, Any, Sequence


def apply_decorators(func: Callable, decorators: Sequence[Callable[..., Any]]) -> Callable:
    for decorator in reversed(decorators):
        func = decorator(func)
    return func

def measure_time(func: Callable):
    @wraps(func)
    def wrapper(task_name:str, *args, **kwargs):
        start_time = time.time()
        result = func(task_name, *args, **kwargs)
        end_time = time.time()
        print(f'-- ran {task_name} in {end_time - start_time:.2f}s --')
        return result
    return wrapper
