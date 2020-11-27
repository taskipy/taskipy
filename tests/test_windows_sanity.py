import unittest


class WindowsSanityTestCase(unittest.TestCase):
    '''
    This test case is a no-op, and exists only to ensure that windows paths work
    as part of the windows sanity ci test.
    '''

    def test_windows_sanity(self):
        print('sanity passed - test was run')
