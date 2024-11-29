"""
Helper, Property and Static method tests for pyubxutils

Created on 26 May 2022

*** NB: must be saved in UTF-8 format ***

@author: semuadmin
"""

# pylint: disable=line-too-long, invalid-name, missing-docstring, no-member

from pathlib import Path
import unittest


class StaticTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        # dirname = os.path.dirname(__file__)
        # self.streamNAV = open(os.path.join(dirname, "pygpsdata-NAV.log"), "rb")

    def tearDown(self):
        # self.streamNAV.close()
        pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
