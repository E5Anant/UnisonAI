import asyncio
import nest_asyncio
from typing import Coroutine, Callable, Any
import functools

def apply_asyncio_patch():
    """Applies the nest_asyncio patch."""
    nest_asyncio.apply()

def run_async_from_sync(coro: Coroutine):
    """Runs a coroutine from a synchronous context."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

def run_sync_in_executor(func: Callable, *args, **kwargs) -> Any:
    """Runs a synchronous function in a thread pool to avoid blocking."""
    loop = asyncio.get_event_loop()
    # functools.partial is used to package the function and its arguments
    p_func = functools.partial(func, *args, **kwargs)
    # The first argument 'None' tells it to use the default ThreadPoolExecutor
    return loop.run_until_complete(loop.run_in_executor(None, p_func))