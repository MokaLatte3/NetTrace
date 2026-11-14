import unittest
from unittest.mock import patch

import nettrace

FAKE_META = {"city": "Manila", "region": "NCR", "country": "Philippines",
             "isp": "Test ISP", "asn": "AS0000"}


@patch("nettrace.formatter.show", create=True)
@patch("nettrace.ip_info.get_metadata", create=True, return_value=FAKE_META)
@patch("nettrace.detection.get_public_ip", create=True)
class TestMain(unittest.TestCase):

    def test_both_ips_found(self, mock_ip, mock_meta, mock_show):
        mock_ip.side_effect = lambda v: "203.0.113.5" if v == 4 else "2001:db8::1"
        self.assertEqual(nettrace.main([]), 0)
        mock_meta.assert_called_once_with("203.0.113.5")
        mock_show.assert_called_once_with("203.0.113.5", "2001:db8::1", FAKE_META)

    def test_ipv6_only_uses_ipv6_for_metadata(self, mock_ip, mock_meta, mock_show):
        mock_ip.side_effect = lambda v: None if v == 4 else "2001:db8::1"
        self.assertEqual(nettrace.main([]), 0)
        mock_meta.assert_called_once_with("2001:db8::1")

    def test_no_ips_returns_1(self, mock_ip, mock_meta, mock_show):
        mock_ip.return_value = None
        self.assertEqual(nettrace.main([]), 1)

    def test_help_exits_cleanly(self, mock_ip, mock_meta, mock_show):
        with self.assertRaises(SystemExit) as ctx:
            nettrace.main(["--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()