import platform
import unittest


@unittest.skipIf(platform.system() != "Windows", "Windows only tests")
class WindowsTestCase(unittest.TestCase):
    def test_windows_path_sanity(self):
        """
        This test case is a no-op, and exists only to ensure that windows paths work
        as part of the windows sanity ci test.
        """
        print("sanity passed - test was run")

    def test_mslex_install(self):
        """Ensure that mslex is installed on Windows"""
        try:
            import mslex  # type: ignore  # noqa: F401
        except ImportError:
            self.fail("Unable to import mslex")

    def test_mslex_import(self):
        """Ensure that mslex is used as shlex"""
        from taskipy.task_runner import shlex

        self.assertEqual(shlex.__name__, "mslex")
