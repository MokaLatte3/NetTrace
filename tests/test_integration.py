import unittest
from unittest.mock import patch, MagicMock

import requests

import nettrace


def fake_response(data):
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = data
    return response


def fake_internet(url, timeout=None):
    # pretend to be ipify and ipapi.co; no IPv6 on this "network"
    if "api6.ipify" in url:
        raise requests.exceptions.ConnectionError()
    if "ipify" in url:
        return fake_response({"ip": "203.0.113.5"})
    if "ipapi.co" in url:
        return fake_response({"city": "Manila", "region": "NCR",
                              "country_name": "Philippines",
                              "org": "Test ISP", "asn": "AS0000"})
    raise AssertionError("unexpected URL: " + url)


class TestIntegration(unittest.TestCase):
    # only the internet is fake: detection, ip_info and formatter are the real code

    @patch("requests.get", side_effect=fake_internet)
    def test_full_run_with_real_modules(self, mock_get):
        with patch("formatter.Console") as mock_console_class:
            exit_code = nettrace.main([])
        self.assertEqual(exit_code, 0)
        mock_console_class.return_value.print.assert_called_once()

    @patch("requests.get", side_effect=requests.exceptions.ConnectionError())
    def test_no_internet_does_not_crash(self, mock_get):
        with patch("formatter.Console"):
            self.assertEqual(nettrace.main([]), 1)


if __name__ == "__main__":
    unittest.main()