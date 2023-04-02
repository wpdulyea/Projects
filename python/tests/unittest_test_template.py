#!/usr/bin/env python3
"""
Description:
"""
# -----------------------------------------------------------------------------
#                               Safe Imports
# -----------------------------------------------------------------------------
# Standard
import unittest
import sys
import os
import re
from time import sleep
from traceback import format_exc
from random import choice, randint, uniform
from datetime import datetime

# Third party

# local


# -----------------------------------------------------------------------------
#                           Global definitions
# -----------------------------------------------------------------------------
__author__ = "Copyright (c) 2022, W P Dulyea, All rights reserved."
__email__ = "wpdulyea@yahoo.com"
__version__ = "$Name: Release 0.1.0 $"[7:-2]


# -----------------------------------------------------------------------------
#                               Test Classes
# -----------------------------------------------------------------------------
class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.string = "foo"
        self.assertIsInstance(self.string, str)

    def test_upper(self):
        self.assertEqual(self.string.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

    def tearDowm(self):
        self.string = None
        self.assertIsNotNone(self.string)

# -----------------------------------------------------------------------------
#                               Test Suites
# -----------------------------------------------------------------------------
def suite() -> unittest.TestSuite:
    suite = unittest.TestSuite()
    suite.addTest(TestStringMethods('test_upper'))
    suite.addTest(TestStringMethods('test_upper'))
    suite.addTest(TestStringMethods('test_split'))

    return suite


# -----------------------------------------------------------------------------
#                               Run as script
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    # unittest.main()
    runner = unittest.TextTestRunner(descriptions=True, verbosity=5)
    runner.run(suite())
