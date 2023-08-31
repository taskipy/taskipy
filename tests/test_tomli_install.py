import subprocess
import sys
import unittest
from typing import Dict, List, Tuple


class TomliInstallTestCase(unittest.TestCase):
    def test_correct_tomli_version_installed(self):
        python_major, python_minor = self.__get_current_python_version()
        packages = self.__get_installed_pip_packages()
        tomli_version = packages.get("tomli")
        v1_regex = r"1.[0-9]+.[0-9]+"
        v2_regex = r"2.[0-9]+.[0-9]+"

        if python_major == 3 and python_minor == 6:
            self.assertRegex(tomli_version, v1_regex)
        elif python_major == 3 and python_minor >= 7:
            self.assertRegex(tomli_version, v2_regex)
        else:
            self.fail("Executed with invalid Python version")

    def __get_current_python_version(self) -> Tuple[int, int]:
        python_version = sys.version_info

        return python_version.major, python_version.minor

    def __get_installed_pip_packages(self) -> Dict[str, str]:
        cmd = "pip list"
        process = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, _ = process.communicate()
        exit_code = process.returncode
        if exit_code != 0:
            raise RuntimeError("listing pip packages got a non-zero exit code")

        result = {}
        packages = self.__remove_pip_list_table_header(stdout.splitlines())
        for package in packages:
            decoded_package = package.decode("utf-8")
            name, version, *_ = decoded_package.split()
            result[name] = version

        return result

    def __remove_pip_list_table_header(self, lines: List[bytes]) -> List[bytes]:
        return lines[2:]
