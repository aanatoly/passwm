import unittest
from passwm import Safe
import sys
import logging

try:
    # Module logging_conf should intialize root logger and, perhaps some
    # others, and assign 'log' variable to proper logger.
    from logging_conf import log
except:
    log = logging.getLogger()
    # log.setLevel(logging.WARNING)
    # log.setLevel(logging.DEBUG)
    # h = logging.StreamHandler()
    # # f = MyFormatter()
    # f = logging.Formatter()
    # h.setFormatter(f)
    # log.addHandler(h)


class TestSafe(unittest.TestCase):
    def setUp(self):
        "self doc"
        # log.debug("\nlog: setUp")
        self.safe = Safe('deadbeaf', '/tmp/xxx')

    def test_upper(self):
        "test_upper doc"
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        "test_isupper doc"
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        "test_split doc"
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


if __name__ == '__main__':
    unittest.main()
