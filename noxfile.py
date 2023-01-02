from typing import List

from poetry.core.factory import Factory

poetry = Factory().create_poetry()
import nox
import nox_poetry

LATEST = "@latest"


def with_python_versions(python_versions: List[str], st_version: str, tqdm_version: str):
    return [(python_version, st_version, tqdm_version) for python_version in python_versions]


PYTHON_ST_TQDM_VERSIONS = (
    with_python_versions(["3.7", "3.8", "3.9"], "~=0.66", "~=4.50")
    + with_python_versions(["3.8", "3.9"], "~=0.66", "~=4.50")
    + with_python_versions(["3.8", "3.9"], "~=1.4", "~=4.50")
    + with_python_versions(["3.8", "3.9"], "~=1.4", "~=4.63")
    + with_python_versions(["3.8", "3.9", "3.10"], "~=1.8", "~=4.63")
    + with_python_versions(["3.8", "3.9", "3.10"], "~=1.12", "~=4.63")
    + with_python_versions(["3.9", "3.10"], "~=1.12", LATEST)
    + with_python_versions(["3.9", "3.10"], LATEST, LATEST)
)


@nox_poetry.session
@nox.parametrize(["python", "streamlit_version", "tqdm_version"], PYTHON_ST_TQDM_VERSIONS)
def tests(session: nox_poetry.Session, streamlit_version, tqdm_version):
    dependencies_to_install_with_pip: List[str] = [
        name if version == LATEST else name + version
        for name, version in [("streamlit", streamlit_version), ("tqdm", tqdm_version)]
    ]

    session.install("pytest", ".")
    session.run("pip", "install", "-U", *dependencies_to_install_with_pip)
    session.run("pytest")


@nox_poetry.session(python=None)
def coverage(session: nox.Session):
    session.install("pytest", "pytest-cov", ".")
    session.run("pytest", "--cov-fail-under=15", "--cov=stqdm", "--cov-report=xml:codecov.xml")


@nox_poetry.session(python=None)
def isort(session: nox.Session):
    session.install("isort")
    session.run("isort", ".", "--check")


@nox_poetry.session(python=None)
def black(session: nox.Session):
    session.install("black")
    session.run("black", ".", "--check")


@nox_poetry.session(python=None)
def lint(session: nox.Session):
    session.install("pylint", "nox", "nox_poetry", "tqdm", "streamlit")
    session.run("pylint", "stqdm", "examples", "tests", "noxfile.py")
