import unittest

from libckan.cache import CKANVersion


class VersionTests(unittest.TestCase):
    def test_comp(self):
        self.assertEqual(CKANVersion("1.1"), CKANVersion("0:1.1"))
        self.assertTrue(CKANVersion("1.2") > CKANVersion("0:1.1"))
        self.assertTrue(CKANVersion("0.2.0") > CKANVersion("0.1.9"))
        self.assertTrue(CKANVersion("v0.2.0") > CKANVersion("v0.1.9"))
        self.assertTrue(CKANVersion("v0.2.1") > CKANVersion("v0.2.0_pre"))
        self.assertTrue(CKANVersion("v0.2.1a") < CKANVersion("v0.2.1b"))
        self.assertTrue(CKANVersion("alpha") < CKANVersion("beta"))
        self.assertTrue(CKANVersion("v6a1") < CKANVersion("v6a2"))
        self.assertTrue(CKANVersion("1.1.1") > CKANVersion("1.1.0.0"))
        self.assertTrue(CKANVersion("1.01") == CKANVersion("1.1"))
        self.assertTrue(CKANVersion("1.0") < CKANVersion("1.0.repackaged") < CKANVersion("1.1.1"))


if __name__ == '__main__':
    unittest.main()
