import unittest

from drive_wiper import format_bytes


class FormatBytesTests(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(format_bytes(0), "0 B")

    def test_bytes(self):
        self.assertEqual(format_bytes(100), "100.0 B")

    def test_kibibytes(self):
        self.assertEqual(format_bytes(1024), "1.0 KiB")

    def test_gibibytes(self):
        self.assertEqual(format_bytes(1024 ** 3), "1.0 GiB")

    def test_invalid_value(self):
        self.assertEqual(format_bytes("unknown"), "Unknown")

    def test_negative_value(self):
        self.assertEqual(format_bytes(-1), "Unknown")


if __name__ == "__main__":
    unittest.main()
