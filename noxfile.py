import re
import subprocess
from typing import Iterable, List

import nox
from packaging.version import Version

LATEST = "@latest"
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


PYTHON_ST_TQDM_VERSIONS = (
    with_python_versions(["3.10", "3.11"], "~=1.29.0", "~=4.61")
    + with_python_versions(["3.10", "3.11", "3.12"], "~=1.29.0", "~=4.66.1")
    + with_python_versions(["3.10", "3.11"], "~=1.29.0", LATEST)
    + with_python_versions(["3.11"], "~=1.41.1", LATEST)
    + with_python_versions(["3.10", "3.11", "3.12"], LATEST, LATEST)
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
def isort(session: nox.Session) -> None:
    install(session, "isort")
    session.run("isort", ".", "--check")


@nox.session(python="3.12")
def black(session: nox.Session) -> None:
    install(session, "black")
    session.run("black", ".", "--check")


@nox.session(python="3.12")
def lint(session: nox.Session) -> None:
    install(session, ".", "pylint", "nox", "tqdm", "streamlit", "pytest", "freezegun")
    session.run("pylint", *tracked_python_files("stqdm", "examples", "tests", "noxfile.py"))
