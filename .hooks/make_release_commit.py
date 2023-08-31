#!/usr/bin/env python3
import subprocess
from pathlib import Path

import tomli


def create_release_commit():
    cwd = Path.cwd()
    with open(cwd / "pyproject.toml", "rb") as file:
        pyproject = tomli.load(file)
    version = pyproject["tool"]["poetry"]["version"]

    p = subprocess.Popen(
        'git add . '
        f'&& git commit -m "Release version {version}" '
        f'&& git tag -a "{version}" -m "Release version {version}" '
        '&& git push && git push --tags',
        shell=True,
        cwd=cwd,
    )

    p.wait()


if __name__ == "__main__":
    create_release_commit()
