import unittest

from libckan.cache import CKANVersion


class VersionTests(unittest.TestCase):
    def test_comp(self):
        self.assertEqual(CKANVersion("1.1"), CKANVersion("0:1.1"))
        self.assertTrue(CKANVersion("1.2") > CKANVersion("0:1.1"))
        self.assertTrue(CKANVersion("0.2.0") > CKANVersion("0.1.9"))
        self.assertTrue(CKANVersion("2:0.2.0") < CKANVersion("3:0.1.9"))


if __name__ == '__main__':
    unittest.main()
