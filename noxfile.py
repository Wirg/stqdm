import string
from typing import List

import nox
import nox_poetry

LATEST = "@latest"


def with_python_versions(python_versions: List[str], st_version: str, tqdm_version: str):
    return [(python_version, st_version, tqdm_version) for python_version in python_versions]


def fix_deps_issues(streamlit_version: str) -> List[str]:
    """
    Fix issues with streamlit and stqdm deps to ease ci
    """
    # Used to avoid a compatibility issue between streamlit and protobuf
    # https://discuss.streamlit.io/t/streamlit-run-with-protobuf-error/25632/5
    protobuf_fix = "protobuf>=3.6.0,!=3.11"
    install_fixes = [protobuf_fix]

    # https://discuss.streamlit.io/t/modulenotfounderror-no-module-named-altair-vegalite-v4/42921/13
    altair_lower_than_5 = "altair<5"
    if streamlit_version != LATEST:
        # We suppose version format to be ~=version, ==version, ...
        if streamlit_version[1] in string.digits:
            streamlit_version = streamlit_version[1:]
        else:
            streamlit_version = streamlit_version[2:]

        st_major, st_minor = streamlit_version.split(".", maxsplit=2)[:2]
        if (int(st_major), int(st_minor)) < (1, 22):
            install_fixes += [altair_lower_than_5]

    return install_fixes


PYTHON_ST_TQDM_VERSIONS = (
    with_python_versions(["3.8", "3.9"], "~=0.66.0", "~=4.50.0")
    + with_python_versions(["3.8", "3.9"], "~=0.66.0", "~=4.50.0")
    + with_python_versions(["3.8", "3.9"], "~=1.4.0", "~=4.50.0")
    + with_python_versions(["3.8", "3.9"], "~=1.4.0", "~=4.63.0")
    + with_python_versions(["3.8", "3.9", "3.10"], "~=1.8.0", "~=4.63.0")
    + with_python_versions(["3.8", "3.9", "3.10"], "~=1.12.0", "~=4.63.0")
    + with_python_versions(["3.9", "3.10"], "~=1.12.0", LATEST)
    + with_python_versions(["3.10"], "~=1.22.0", LATEST)
    + with_python_versions(["3.9", "3.10"], LATEST, LATEST)
)


@nox_poetry.session
@nox.parametrize(["python", "streamlit_version", "tqdm_version"], PYTHON_ST_TQDM_VERSIONS)
def tests(session: nox_poetry.Session, streamlit_version: str, tqdm_version: str) -> None:
    dependencies_to_install_with_pip: List[str] = [
        name if version == LATEST else name + version
        for name, version in [("streamlit", streamlit_version), ("tqdm", tqdm_version)]
    ]

    session.install("pytest", ".")
    session.run("pip", "install", "-U", *dependencies_to_install_with_pip, *fix_deps_issues(streamlit_version))
    session.run("pytest")


@nox_poetry.session(python=None)
def coverage(session: nox.Session) -> None:
    session.install("pytest", "pytest-cov", ".")
    session.run("pytest", "--cov-fail-under=15", "--cov=stqdm", "--cov-report=xml:codecov.xml")


@nox_poetry.session(python=None)
def isort(session: nox.Session):
    session.install("isort")
    session.run("isort", ".", "--check")


@nox_poetry.session(python=None)
def black(session: nox.Session) -> None:
    session.install("black")
    session.run("black", ".", "--check")


@nox_poetry.session(python=None)
def lint(session: nox.Session) -> None:
    session.install("pylint", "nox", "nox_poetry", "tqdm", "streamlit")
    session.run("pylint", "stqdm", "examples", "tests", "noxfile.py")
