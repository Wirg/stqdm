import hashlib
import string
from pathlib import Path
from typing import List

import nox
import nox_poetry
from nox_poetry.poetry import CommandSkippedError
from packaging.version import Version

LATEST = "@latest"


def is_version_below(target: tuple[int, int], version: str) -> bool:
    if version == LATEST:
        return False
    # We suppose version format to be ~=version, ==version, >version, ...
    if version[0] in string.digits:
        pass
    elif version[1] in string.digits:
        version = version[1:]
    else:
        version = version[2:]

    version = Version(version)
    return version < Version(f"{target[0]}.{target[1]}")


def with_python_versions(python_versions: List[str], st_version: str, tqdm_version: str):
    return [(python_version, st_version, tqdm_version) for python_version in python_versions]


def fix_deps_issues(streamlit_version: str) -> List[str]:
    """
    Fix issues with streamlit and stqdm deps to ease ci
    """
    install_fixes: List[str] = []

    # https://discuss.streamlit.io/t/modulenotfounderror-no-module-named-altair-vegalite-v4/42921/13
    altair_lower_than_5 = "altair<5"
    if is_version_below((1, 22), streamlit_version):
        install_fixes += [altair_lower_than_5]

    return install_fixes


def has_poetry_lock_changed_since_last_run(tmpdir: Path) -> bool:
    hashfile = tmpdir / "poetry.lock.hash"
    lockdata = Path("poetry.lock").read_bytes()
    digest = hashlib.blake2b(lockdata).hexdigest()

    if not hashfile.is_file() or hashfile.read_text() != digest:
        hashfile.write_text(digest)
        return True
    return False


def export_poetry_constraints_file(session: nox_poetry.Session, constraints_path: Path, groups: list[str]) -> None:
    """Use poetry export to generate a constraints file with only the specified groups"""
    output = session.run_always(
        "poetry",
        "export",
        "--format=constraints.txt",
        "--only",
        ",".join(groups),
        "--output",
        str(constraints_path),
        "--without-hashes",
        external=True,
        silent=True,
        stderr=None,
    )
    if output is None:
        raise CommandSkippedError("The command `poetry export` was not executed")


def build_dependencies_to_install_list(
    streamlit_version: str, tqdm_version: str, other_package_to_install: list[str]
) -> List[str]:
    dependencies_to_install_with_pip: List[str] = [
        name if version == LATEST else name + version
        for name, version in [("streamlit", streamlit_version), ("tqdm", tqdm_version)]
    ]
    dependencies_to_install_with_pip += fix_deps_issues(streamlit_version)
    dependencies_to_install_with_pip += other_package_to_install
    return dependencies_to_install_with_pip


def install_deps(session: nox.Session, constraint_groups: List[str], dependencies_to_install: List[str]) -> None:
    """
    Do not use nox_poetry directly as it will install the dependencies based on the lock files.
    If we force install with pip afterwards we risk to have unconstrained versions and we will reinstall everytime:
    poetry will notice a change and reinstall and pip will notice a change and reinstall.
    """
    tmpdir = Path(session.create_tmp())
    constraints_path = tmpdir / "constraints.txt"

    if has_poetry_lock_changed_since_last_run(tmpdir):
        export_poetry_constraints_file(
            session,
            constraints_path,
            constraint_groups,
        )

    session.install("--upgrade", f"--constraint={constraints_path}", *dependencies_to_install)


PYTHON_ST_TQDM_VERSIONS = (
    # python = ">=3.10,<4.0" # current 3.13.1
    # tqdm = ">=4.61" # current 4.67.1
    # streamlit = ">=1.29.0" # current # 1.41.1
    with_python_versions(["3.10", "3.11"], "~=1.29.0", "~=4.61")
    + with_python_versions(["3.10", "3.11"], "~=1.29.0", "~=4.66.1")
    + with_python_versions(["3.10", "3.11", "3.12"], "~=1.29.0", "~=4.66.1")
    + with_python_versions(["3.10", "3.11"], "~=1.29.0", LATEST)
    + with_python_versions(["3.11"], "~=1.41.1", LATEST)
    + with_python_versions(["3.10", "3.11", "3.12"], LATEST, LATEST)
)


@nox.session
@nox.parametrize(["python", "streamlit_version", "tqdm_version"], PYTHON_ST_TQDM_VERSIONS)
def tests(session: nox.Session, streamlit_version: str, tqdm_version: str) -> None:
    dependencies_to_install = build_dependencies_to_install_list(streamlit_version, tqdm_version, [".", "pytest", "freezegun"])
    install_deps(session, constraint_groups=["dev"], dependencies_to_install=dependencies_to_install)
    session.run("pytest", "-m", "not demo_app")


@nox.session(python=None)
@nox.parametrize(["python", "streamlit_version", "tqdm_version"], [PYTHON_ST_TQDM_VERSIONS[-1]])
def test_demo_app(session: nox.Session, streamlit_version: str, tqdm_version: str) -> None:
    dependencies_to_install = build_dependencies_to_install_list(streamlit_version, tqdm_version, [".", "pytest", "freezegun"])
    install_deps(session, constraint_groups=["dev"], dependencies_to_install=dependencies_to_install)
    session.run("pytest", "-m", "demo_app")


@nox.session(python=None)
@nox.parametrize(["python", "streamlit_version", "tqdm_version"], [PYTHON_ST_TQDM_VERSIONS[0]] + [PYTHON_ST_TQDM_VERSIONS[-1]])
def coverage(session: nox.Session, streamlit_version: str, tqdm_version: str) -> None:
    dependencies_to_install = build_dependencies_to_install_list(
        streamlit_version, tqdm_version, [".", "pytest", "pytest-cov", "freezegun"]
    )
    install_deps(session, constraint_groups=["dev"], dependencies_to_install=dependencies_to_install)
    session.run("pytest", "--cov-fail-under=15", "--cov=stqdm", "--cov-report=xml:codecov.xml", "-m", "not demo_app")


@nox.session(python=None)
def isort(session: nox_poetry.Session):
    session.install("isort")
    session.run("isort", ".", "--check")


@nox_poetry.session(python=None)
def black(session: nox_poetry.Session) -> None:
    session.install("black")
    session.run("black", ".", "--check")


@nox_poetry.session(python=None)
def lint(session: nox_poetry.Session) -> None:
    session.install("pylint", "nox", "nox_poetry", "tqdm", "streamlit", "pytest", "freezegun")
    session.run("pylint", "stqdm", "examples", "tests", "noxfile.py")
