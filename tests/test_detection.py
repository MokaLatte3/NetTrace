"""Tests for detection.get_public_ip. Every requests.get call is mocked."""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import requests

# detection.py lives one folder up. Adding it to the path lets this file run
# both via "python -m unittest" and directly as "python tests/test_detection.py".
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import detection  # noqa: E402


def fake_response(status_code=200, json_data=None, json_error=None):
    """Build a stand-in for a requests.Response."""
    response = MagicMock()
    response.status_code = status_code
    if json_error is not None:
        response.json.side_effect = json_error
    else:
        response.json.return_value = json_data
    return response


# Patch where detection looks it up, so no real network call can slip through.
@patch("detection.requests.get")
class GetPublicIpTests(unittest.TestCase):

    def test_ipv4_success(self, mock_get):
        mock_get.return_value = fake_response(json_data={"ip": "203.0.113.5"})

        self.assertEqual(detection.get_public_ip(4), "203.0.113.5")
        mock_get.assert_called_once_with(
            "https://api.ipify.org?format=json", timeout=5
        )

    def test_ipv6_success(self, mock_get):
        mock_get.return_value = fake_response(json_data={"ip": "2001:db8::1"})

        self.assertEqual(detection.get_public_ip(6), "2001:db8::1")
        mock_get.assert_called_once_with(
            "https://api6.ipify.org?format=json", timeout=5
        )

    def test_timeout_returns_none(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout

        self.assertIsNone(detection.get_public_ip(4))

    def test_connection_error_returns_none(self, mock_get):
        # This is also what happens on a network with no IPv6.
        mock_get.side_effect = requests.exceptions.ConnectionError

        self.assertIsNone(detection.get_public_ip(6))
   
    def test_unexpected_error_returns_none(self, mock_get):
        # Even an error we never planned for must not crash the CLI.
        mock_get.side_effect = RuntimeError("something unexpected")

        self.assertIsNone(detection.get_public_ip(4))

    def test_non_200_returns_none(self, mock_get):
        mock_get.return_value = fake_response(
            status_code=503, json_data={"ip": "203.0.113.5"}
        )

        self.assertIsNone(detection.get_public_ip(4))

    def test_bad_json_returns_none(self, mock_get):
        mock_get.return_value = fake_response(json_error=ValueError("bad json"))

        self.assertIsNone(detection.get_public_ip(4))

    def test_missing_ip_key_returns_none(self, mock_get):
        mock_get.return_value = fake_response(json_data={"address": "203.0.113.5"})

        self.assertIsNone(detection.get_public_ip(4))

    def test_wrong_json_shape_returns_none(self, mock_get):
        for data in ([], {"ip": None}, {"ip": 12345}, {"ip": ""}):
            with self.subTest(data=data):
                mock_get.return_value = fake_response(json_data=data)
                self.assertIsNone(detection.get_public_ip(4))

    def test_not_an_ip_address_returns_none(self, mock_get):
        for text in ("not-an-ip", "999.1.1.1", "203.0.113", "<html>"):
            with self.subTest(text=text):
                mock_get.return_value = fake_response(json_data={"ip": text})
                self.assertIsNone(detection.get_public_ip(4))

    def test_wrong_ip_family_returns_none(self, mock_get):
        # An IPv6 address for an IPv4 request (and vice versa) is never valid.
        mock_get.return_value = fake_response(json_data={"ip": "2001:db8::1"})
        self.assertIsNone(detection.get_public_ip(4))

        mock_get.return_value = fake_response(json_data={"ip": "203.0.113.5"})
        self.assertIsNone(detection.get_public_ip(6))

    def test_invalid_version_returns_none(self, mock_get):
        for version in (5, 0, "4", None, [4]):
            with self.subTest(version=version):
                self.assertIsNone(detection.get_public_ip(version))
        # A bad version should be rejected before touching the network.
        mock_get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
