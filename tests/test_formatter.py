import unittest
from unittest.mock import patch
from rich.console import Console
from formatter import show

class TestFormatter(unittest.TestCase):
    def setUp(self):
        self.console = Console(record=True, width=100)

        self.console_patch = patch('formatter.Console', return_value=self.console)

        self.console_patch.start()
        self.addCleanup(self.console_patch.stop)

    def get_console_output(self):
        return self.console.export_text()

    def test_valid_ipv4_and_ipv6(self):
        metadata = {
            "city": "Imus City",
            "region": "Cavite",
            "country": "Philippines",
            "isp": "Globe Telecom",
            "asn": "AS9829"
        }

        result = show("103.60.171.44", "2001:4860:7:80c::f2", metadata)
        output = self.get_console_output()

        self.assertIsNone(result)
        self.assertIn("103.60.171.44", output)
        self.assertIn("2001:4860:7:80c::f2", output)
        self.assertIn("Imus City", output)
        self.assertIn("Cavite", output)
        self.assertIn("Philippines", output)
        self.assertIn("Globe Telecom", output)
        self.assertIn("AS9829", output)

    def test_ipv4_none(self):
        show(None, "2001:4680:7:80c::f2", {})

        output = self.get_console_output()

        self.assertIn("N/A", output)
        self.assertIn("2001:4680:7:80c::f2", output)

    def test_ipv6_none(self):
        show("103.60.171.44", None, {})

        output = self.get_console_output()

        self.assertIn("103.60.171.44", output)
        self.assertIn("N/A", output)

    def test_both_no_ip(self):
        show(None, None, {})

        output = self.get_console_output()

        self.assertEqual(output.count("N/A"), 7)

    def test_empty_metadata(self):
        show("103.60.171.44", "2001:4680:7:80c::f2", {})

        output = self.get_console_output()

        self.assertIn("N/A", output)

    def test_metadata_none(self):
        show("103.60.171.44", "2001:4680:7:80c::f2", None)

        output = self.get_console_output()

        self.assertIn("N/A", output)

    def test_individual_missing_metadata_fields(self):
        metadata = {
            "city": "Imus City",
            "country": "Philippines",
        }

        show("103.60.171.44", "2001:4860:7:80c::f2", metadata)

        output = self.get_console_output()

        self.assertIn("Imus City", output)
        self.assertIn("Philippines", output)
        self.assertIn("N/A", output) 

    def test_required_rows_are_displayed(self):
        show("103.60.171.44", "2001:4680:7:80c::f2", {})

        output = self.get_console_output()

        expected_rows = [
            "IPv4 Address",
            "IPv6 Address",
            "City",
            "Region",
            "Country",
            "ISP",
            "ASN"
        ]

        for row in expected_rows:
            with self.subTest(row=row):
                self.assertIn(row, output)

if __name__ == '__main__':
    unittest.main()
