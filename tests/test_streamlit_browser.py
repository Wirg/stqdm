from __future__ import annotations

# pylint: disable=missing-function-docstring,redefined-outer-name
import contextlib
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterator
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

import pytest

pytest.importorskip("playwright")
from playwright.sync_api import Browser, Page, sync_playwright

pytestmark = pytest.mark.browser_smoke

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "demo" / "app" / "Home.py"


@contextlib.contextmanager
def run_streamlit_app() -> Iterator[str]:
    port = _get_free_port()
    app_url = f"http://127.0.0.1:{port}"
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(APP_PATH),
        "--server.address",
        "127.0.0.1",
        "--server.port",
        str(port),
        "--server.headless",
        "true",
        "--server.fileWatcherType",
        "none",
        "--browser.gatherUsageStats",
        "false",
    ]
    env = os.environ.copy()
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )
    try:
        _wait_for_server(app_url, process)
        yield app_url
    finally:
        _stop_process(process)


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _wait_for_server(app_url: str, process: subprocess.Popen[str], timeout_seconds: float = 30.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            break
        try:
            with urlopen(app_url, timeout=1):  # noqa: S310
                return
        except (URLError, TimeoutError, ConnectionError, OSError) as exc:
            last_error = exc
            time.sleep(0.2)
    output = _read_process_output(process)
    raise RuntimeError(f"Streamlit app did not start at {app_url}.\n{output}") from last_error


def _read_process_output(process: subprocess.Popen[str]) -> str:
    if process.stdout is None:
        return ""
    process.terminate()
    with contextlib.suppress(subprocess.TimeoutExpired):
        return process.communicate(timeout=5)[0]
    return ""


def _stop_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    with contextlib.suppress(subprocess.TimeoutExpired):
        process.wait(timeout=5)
        return
    process.kill()
    with contextlib.suppress(subprocess.TimeoutExpired):
        process.wait(timeout=5)


@pytest.fixture(scope="module")
def streamlit_app_url() -> Iterator[str]:
    with run_streamlit_app() as app_url:
        yield app_url


@pytest.fixture(scope="module")
def browser() -> Iterator[Browser]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture()
def page(browser: Browser) -> Iterator[Page]:
    context = browser.new_context(viewport={"width": 1440, "height": 1200})
    page = context.new_page()
    yield page
    context.close()


def _wait_for_heading(page: Page, heading: str) -> None:
    page.get_by_role("heading", name=heading).wait_for(timeout=30_000)


def _progress_bars(page: Page):
    return page.locator('[data-testid="stProgressBar"]')


def _goto_page(page: Page, streamlit_app_url: str, path: str) -> None:
    page.goto(f"{streamlit_app_url}/{path.lstrip('/')}", wait_until="domcontentloaded")


def test_home_page_loads_with_main_progress(page: Page, streamlit_app_url: str) -> None:
    page.goto(streamlit_app_url, wait_until="domcontentloaded")

    _wait_for_heading(page, "Use stqdm in the main area")
    bars = _progress_bars(page)
    bars.first.wait_for(timeout=30_000)

    assert bars.count() >= 1
    assert urlparse(page.url).path in {"", "/"}


def test_navigation_to_sidebar_page_renders_sidebar_progress(page: Page, streamlit_app_url: str) -> None:
    page.goto(streamlit_app_url, wait_until="domcontentloaded")
    page.locator('section[data-testid="stSidebar"]').get_by_role("link", name="Use stqdm in the sidebar").click()

    _wait_for_heading(page, "Use stqdm in the sidebar")
    sidebar = page.locator('section[data-testid="stSidebar"]')
    sidebar.wait_for(timeout=30_000)
    sidebar_bars = sidebar.locator('[data-testid="stProgressBar"]')
    sidebar_bars.first.wait_for(timeout=30_000)

    assert sidebar_bars.count() >= 1
    assert urlparse(page.url).path.endswith("/stqdm_in_sidebar")


def test_columns_page_renders_multiple_progress_bars(page: Page, streamlit_app_url: str) -> None:
    _goto_page(page, streamlit_app_url, "stqdm_in_columns")

    _wait_for_heading(page, "Use stqdm in columns")
    bars = _progress_bars(page)
    bars.first.wait_for(timeout=30_000)

    assert bars.count() >= 3
    assert urlparse(page.url).path.endswith("/stqdm_in_columns")


def test_multi_bars_page_renders_three_columns_of_progress(page: Page, streamlit_app_url: str) -> None:
    _goto_page(page, streamlit_app_url, "stqdm_multi_bars_in_columns")

    _wait_for_heading(page, "Multiple bars in columns")
    bars = _progress_bars(page)
    bars.first.wait_for(timeout=30_000)

    assert bars.count() >= 3
    assert urlparse(page.url).path.endswith("/stqdm_multi_bars_in_columns")


def test_patch_tqdm_auto_page_shows_patched_status(page: Page, streamlit_app_url: str) -> None:
    _goto_page(page, streamlit_app_url, "stqdm_patch_tqdm")

    _wait_for_heading(page, "Patch tqdm.auto")
    page.get_by_text("tqdm.auto.tqdm is patched: True").wait_for(timeout=30_000)

    assert urlparse(page.url).path.endswith("/stqdm_patch_tqdm")


def test_scoped_configuration_page_shows_desc_in_custom_bar(page: Page, streamlit_app_url: str) -> None:
    _goto_page(page, streamlit_app_url, "stqdm_scopes")

    _wait_for_heading(page, "Scoped configuration")
    page.get_by_text("Hello Scoped").wait_for(timeout=30_000)
    bars = _progress_bars(page)
    bars.first.wait_for(timeout=30_000)

    assert bars.count() >= 2
    assert urlparse(page.url).path.endswith("/stqdm_scopes")


def test_bar_format_page_shows_desc_text_when_requested(page: Page, streamlit_app_url: str) -> None:
    _goto_page(page, streamlit_app_url, "stqdm_bar_format")

    _wait_for_heading(page, "bar_format values")
    page.get_by_text("controls how tqdm formats the text around the bar").wait_for(timeout=30_000)
    page.get_by_role("combobox").click()
    page.get_by_role("option", name="{desc} {percentage:.0f}%", exact=True).click()
    page.get_by_text("Format 100%").wait_for(timeout=30_000)

    assert urlparse(page.url).path.endswith("/stqdm_bar_format")
