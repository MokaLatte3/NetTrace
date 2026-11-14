"""Find this computer's public IP address using the ipify service."""

import requests

# ipify serves each IP family from its own hostname. api6 can only be reached
# over IPv6, so on a network without IPv6 the request simply fails, and that
# tells us "no IPv6" without any extra checks.
IPV4_URL = "https://api.ipify.org?format=json"
IPV6_URL = "https://api6.ipify.org?format=json"

# Without a timeout a dead network could hang the whole CLI.
TIMEOUT_SECONDS = 5


def get_public_ip(version):
    """Return the public IP for version 4 or 6 as a string, or None."""
    if version == 4:
        url = IPV4_URL
    elif version == 6:
        url = IPV6_URL
    else:
        return None

    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
        if response.status_code != 200:
            return None
        data = response.json()
    # RequestException covers no internet, timeouts and DNS failures.
    # ValueError covers a body that is not valid JSON.
    # The caller expects None on failure, never an exception.
    except (requests.RequestException, ValueError):
        return None

    return _extract_ip(data)


def _extract_ip(data):
    """Pull the "ip" string out of the JSON, or None if it isn't there."""
    # Valid JSON can still be the wrong shape (a list, or "ip": null), and the
    # contract promises a string, so check before trusting it.
    if not isinstance(data, dict):
        return None
    ip = data.get("ip")
    if not isinstance(ip, str) or not ip:
        return None
    return ip
