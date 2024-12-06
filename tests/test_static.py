"""
Helper, Property and Static method tests for pyubxutils

Created on 26 May 2022

*** NB: must be saved in UTF-8 format ***

@author: semuadmin
"""

# pylint: disable=line-too-long, invalid-name, missing-docstring, no-member

from pathlib import Path
import unittest
from pyubxutils.helpers import h2sphp, ll2sphp


class StaticTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        # dirname = os.path.dirname(__file__)
        # self.streamNAV = open(os.path.join(dirname, "pygpsdata-NAV.log"), "rb")

    def tearDown(self):
        # self.streamNAV.close()
        pass

    def testll2sphp(self):
        res = ll2sphp(45.123456789)
        self.assertEqual(res, (451234567, 89))
        res = ll2sphp(45.123456789012)
        self.assertEqual(res, (451234567, 89))

    def testh2sphp(self):
        res = h2sphp(1234567.89)
        self.assertEqual(res, (1234567, 89))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
