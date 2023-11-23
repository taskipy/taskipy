#!/usr/bin/env python3
import tomli
import secrets
import subprocess
from pathlib import Path


def create_release_commit():
    cwd = Path.cwd()
    with open(cwd / "pyproject.toml", "rb") as file:
        pyproject = tomli.load(file)
    version = pyproject["tool"]["poetry"]["version"]
    branch = f"release-{version}-{secrets.token_hex(12)}"

    p = subprocess.Popen(
        " && ".join[
            f"git checkout -b {branch}",
            "git add .",
            f'git commit -m "Release version {version}"',
            f'git tag -a "{version}" -m "Release version {version}"',
            f"git push --set-upstream origin {branch}",
            f"git push --tags",
        ],
        shell=True,
        cwd=cwd,
    )

    p.wait()


if __name__ == "__main__":
    create_release_commit()
