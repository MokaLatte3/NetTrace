# Tests for ip_info.py. requests.get is mocked everywhere so these never
# touch the internet.

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import requests

# so "import ip_info" works even when the tests are run from inside tests/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ip_info  # noqa: E402

KEYS = {"city", "region", "country", "isp", "asn"}
ALL_NA = {"city": "N/A", "region": "N/A", "country": "N/A", "isp": "N/A", "asn": "N/A"}


def fake_response(status=200, json_data=None, bad_json=False):
    # pretend to be the response object that requests.get would give back
    response = MagicMock()
    response.status_code = status
    if bad_json:
        response.json.side_effect = ValueError("not json")
    else:
        response.json.return_value = json_data
    return response


class TestGetMetadata(unittest.TestCase):

    @patch("ip_info.requests.get")
    def test_full_success(self, mock_get):
        mock_get.return_value = fake_response(json_data={
            "city": "Manila",
            "region": "Metro Manila",
            "country_name": "Philippines",
            "org": "Example Telecom",
            "asn": "AS12345",
        })

        result = ip_info.get_metadata("8.8.8.8")

        self.assertEqual(result, {
            "city": "Manila",
            "region": "Metro Manila",
            "country": "Philippines",
            "isp": "Example Telecom",
            "asn": "AS12345",
        })
        # also check we used the right URL and the 5 second timeout
        mock_get.assert_called_once_with("https://ipapi.co/8.8.8.8/json/", timeout=5)

    @patch("ip_info.requests.get")
    def test_partially_missing_fields(self, mock_get):
        # city is missing, region is empty, org is null
        mock_get.return_value = fake_response(json_data={
            "region": "",
            "country_name": "Philippines",
            "org": None,
            "asn": "AS12345",
        })

        result = ip_info.get_metadata("8.8.8.8")

        self.assertEqual(set(result), KEYS)
        self.assertEqual(result["city"], "N/A")
        self.assertEqual(result["region"], "N/A")
        self.assertEqual(result["isp"], "N/A")
        self.assertEqual(result["country"], "Philippines")
        self.assertEqual(result["asn"], "AS12345")

    @patch("ip_info.requests.get")
    def test_rate_limit_429(self, mock_get):
        mock_get.return_value = fake_response(status=429)
        self.assertEqual(ip_info.get_metadata("8.8.8.8"), ALL_NA)

    @patch("ip_info.requests.get")
    def test_other_non_200(self, mock_get):
        mock_get.return_value = fake_response(status=500)
        self.assertEqual(ip_info.get_metadata("8.8.8.8"), ALL_NA)

    @patch("ip_info.requests.get")
    def test_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout()
        self.assertEqual(ip_info.get_metadata("8.8.8.8"), ALL_NA)

    @patch("ip_info.requests.get")
    def test_no_internet(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError()
        self.assertEqual(ip_info.get_metadata("8.8.8.8"), ALL_NA)

    @patch("ip_info.requests.get")
    def test_bad_json(self, mock_get):
        mock_get.return_value = fake_response(bad_json=True)
        self.assertEqual(ip_info.get_metadata("8.8.8.8"), ALL_NA)

    @patch("ip_info.requests.get")
    def test_error_true_in_body(self, mock_get):
        # status is 200 but the body says error, should still be all N/A
        mock_get.return_value = fake_response(
            json_data={"error": True, "reason": "RateLimited", "city": "Manila"}
        )
        self.assertEqual(ip_info.get_metadata("8.8.8.8"), ALL_NA)

    @patch("ip_info.requests.get")
    def test_ip_none_skips_api(self, mock_get):
        self.assertEqual(ip_info.get_metadata(None), ALL_NA)
        mock_get.assert_not_called()

    @patch("ip_info.requests.get")
    def test_ip_empty_skips_api(self, mock_get):
        self.assertEqual(ip_info.get_metadata(""), ALL_NA)
        mock_get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
