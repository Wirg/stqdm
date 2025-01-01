import time


def long_running_task(seconds: float) -> None:
    """Simulate a long running task."""
    time.sleep(seconds)
