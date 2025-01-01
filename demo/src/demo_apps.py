# pylint: disable=import-outside-toplevel
# We import inside the functions to be able to use streamlit.testing.AppTest.from_function


def simple_stqdm_in_main(stop_iterations: int = 10, total_iterations: int = 50, task_duration: float = 5) -> None:
    """Simple example using stqdm with a standard for loop and iterator in st.main."""
    from demo.src.utils import long_running_task
    from stqdm import stqdm

    for _ in stqdm(range(0, stop_iterations), total=total_iterations):
        long_running_task(task_duration)
