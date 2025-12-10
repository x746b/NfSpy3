import unittest


@unittest.skip("NfSpy integration tests require FUSE bindings and an NFS target.")
class NfSpyTestCase(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main(argv=['NfSpyTestCase'])
