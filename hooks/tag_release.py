#!/usr/bin/env python3
import toml
import subprocess
import os
from os import path

def create_release_commit():
    pyproject = toml.load(path.join(os.curdir, 'pyproject.toml'))
    version = pyproject['tool']['poetry']['version']

    p = subprocess.Popen(f'git add . && git commit -m "Release version {version}" && git tag -a "{version}" -m "Release version {version}" && git push && git push --tags',
                         shell=True,
                         cwd=os.curdir)

    p.wait()

if __name__ == '__main__':
    create_release_commit()

