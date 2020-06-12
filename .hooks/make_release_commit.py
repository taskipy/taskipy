#!/usr/bin/env python3
import toml
import subprocess
from pathlib import Path

def create_release_commit():
    cwd = Path.cwd()
    pyproject = toml.load(cwd / 'pyproject.toml')
    version = pyproject['tool']['poetry']['version']

    p = subprocess.Popen(f'git add . && git commit -m "Release version {version}" && git tag -a "{version}" -m "Release version {version}" && git push && git push --tags',
                         shell=True,
                         cwd=cwd)

    p.wait()

if __name__ == '__main__':
    create_release_commit()

