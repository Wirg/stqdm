import string

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


if __name__ == "__main__":
    assert not is_version_below((1, 22), LATEST)
    assert not is_version_below((1, 22), "1.22.1")
    assert is_version_below((1, 22), "1.19.1")
    assert not is_version_below((1, 22), "~=1.24")
    assert not is_version_below((1, 22), ">=1.24")
    assert is_version_below((1, 22), "~=1.20")
