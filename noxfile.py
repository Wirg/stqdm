import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable, List

import nox
from packaging.version import Version

LATEST = "@latest"
COMMITIZEN_ADOPTION_BASE = "33e5301a3f31ec88edf533b2eed80f38d1573345"
nox.options.default_venv_backend = "uv|virtualenv"


def is_version_below(target: tuple[int, int], version: str) -> bool:
    if version == LATEST:
        return False
    version = re.sub(r"^[^\d]+", "", version)
    return Version(version) < Version(f"{target[0]}.{target[1]}")


def with_python_versions(python_versions: Iterable[str], streamlit_version: str, tqdm_version: str):
    return [(python_version, streamlit_version, tqdm_version) for python_version in python_versions]


def fix_deps_issues(streamlit_version: str) -> List[str]:
    install_fixes: List[str] = []
    if is_version_below((1, 22), streamlit_version):
        install_fixes.append("altair<5")
    return install_fixes


def dependency(name: str, version: str) -> str:
    return name if version == LATEST else f"{name}{version}"


def build_dependencies_to_install_list(
    streamlit_version: str, tqdm_version: str, other_packages_to_install: list[str]
) -> List[str]:
    dependencies_to_install = [
        dependency("streamlit", streamlit_version),
        dependency("tqdm", tqdm_version),
    ]
    dependencies_to_install += fix_deps_issues(streamlit_version)
    dependencies_to_install += other_packages_to_install
    return dependencies_to_install


def install(session: nox.Session, *dependencies: str) -> None:
    session.install(*dependencies)


def tracked_python_files(*paths: str) -> list[str]:
    files = subprocess.check_output(["git", "ls-files", *paths], text=True).splitlines()
    return [file for file in files if file.endswith(".py")]


def git_ref_exists(ref: str) -> bool:
    return subprocess.run(["git", "rev-parse", "--verify", "--quiet", ref], check=False).returncode == 0


def git_is_ancestor(ancestor: str, descendant: str) -> bool:
    if not git_ref_exists(ancestor) or not git_ref_exists(descendant):
        return False
    return subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, descendant], check=False).returncode == 0


def commitizen_range_start(base: str, head: str) -> str:
    adoption_base = os.environ.get("COMMITIZEN_ADOPTION_BASE", COMMITIZEN_ADOPTION_BASE)
    if git_is_ancestor(adoption_base, head) and not git_is_ancestor(adoption_base, base):
        return adoption_base
    return base


def commitizen_rev_range() -> str:
    """Build the commit range that should be checked by Commitizen."""
    explicit_rev_range = os.environ.get("COMMITIZEN_REV_RANGE")
    if explicit_rev_range:
        return explicit_rev_range

    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if event_path:
        with open(event_path, encoding="utf-8") as event_file:
            event = json.load(event_file)
        if "pull_request" in event:
            base = event["pull_request"]["base"]["sha"]
            head = event["pull_request"]["head"]["sha"]
            return f"{commitizen_range_start(base, head)}..{head}"
        before = event.get("before")
        after = event.get("after")
        if before and after and set(before) != {"0"}:
            return f"{commitizen_range_start(before, after)}..{after}"

    return "HEAD~1..HEAD"


PYTHON_ST_TQDM_VERSIONS = (
    with_python_versions(["3.10", "3.11"], "~=1.29.0", "~=4.61")
    + with_python_versions(["3.10", "3.11", "3.12"], "~=1.29.0", "~=4.66.1")
    + with_python_versions(["3.10", "3.11"], "~=1.29.0", LATEST)
    + with_python_versions(["3.11"], "~=1.41.1", LATEST)
    + with_python_versions(["3.10", "3.11", "3.12", "3.13"], LATEST, LATEST)
)


@nox.session
@nox.parametrize(["python", "streamlit_version", "tqdm_version"], PYTHON_ST_TQDM_VERSIONS)
def tests(session: nox.Session, streamlit_version: str, tqdm_version: str) -> None:
    dependencies_to_install = build_dependencies_to_install_list(streamlit_version, tqdm_version, [".", "pytest", "freezegun"])
    install(session, *dependencies_to_install)
    session.run("pytest", "-m", "not demo_app")


@nox.session
@nox.parametrize(["python", "streamlit_version", "tqdm_version"], [PYTHON_ST_TQDM_VERSIONS[-1]])
def test_demo_app(session: nox.Session, streamlit_version: str, tqdm_version: str) -> None:
    dependencies_to_install = build_dependencies_to_install_list(streamlit_version, tqdm_version, [".", "pytest", "freezegun"])
    install(session, *dependencies_to_install)
    session.run("pytest", "-m", "demo_app")


@nox.session
@nox.parametrize(["python", "streamlit_version", "tqdm_version"], [PYTHON_ST_TQDM_VERSIONS[0], PYTHON_ST_TQDM_VERSIONS[-1]])
def coverage(session: nox.Session, streamlit_version: str, tqdm_version: str) -> None:
    dependencies_to_install = build_dependencies_to_install_list(
        streamlit_version, tqdm_version, [".", "pytest", "pytest-cov", "freezegun"]
    )
    install(session, *dependencies_to_install)
    session.run("pytest", "--cov-fail-under=15", "--cov=stqdm", "--cov-report=xml:codecov.xml", "-m", "not demo_app")


@nox.session(python="3.12")
def ruff_format(session: nox.Session) -> None:
    install(session, "ruff")
    session.run("ruff", "format", ".", "--check")


@nox.session(python="3.12")
def ruff_check(session: nox.Session) -> None:
    install(session, "ruff")
    session.run("ruff", "check", ".")


@nox.session(python="3.12")
def lint(session: nox.Session) -> None:
    install(session, ".", "pylint", "nox", "tqdm", "streamlit", "pytest", "freezegun")
    session.run("pylint", *tracked_python_files("stqdm", "examples", "tests", "noxfile.py"))


@nox.session(python="3.12")
def commitlint(session: nox.Session) -> None:
    install(session, "commitizen")
    session.run("cz", "check", "--rev-range", commitizen_rev_range())


@nox.session(python="3.12")
def release(session: nox.Session) -> None:
    """Build and validate release artifacts."""
    install(session, "twine", "check-wheel-contents")

    dist_dir = Path(session.create_tmp()) / "dist"
    session.run("uv", "build", "--out-dir", str(dist_dir), external=True)

    distributions = sorted(str(path) for path in dist_dir.iterdir() if path.suffix in {".gz", ".whl"})
    wheels = [dist for dist in distributions if dist.endswith(".whl")]
    session.run("twine", "check", "--strict", *distributions)
    session.run("check-wheel-contents", *wheels)

    with tempfile.TemporaryDirectory() as venv_dir:
        session.run(sys.executable, "-m", "venv", venv_dir, external=True)
        venv_python = Path(venv_dir) / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        session.run(str(venv_python), "-m", "pip", "install", wheels[0], external=True)
        session.run(
            str(venv_python),
            "-c",
            "from importlib.metadata import version; import stqdm; assert stqdm.__version__ == version('stqdm')",
            external=True,
        )
