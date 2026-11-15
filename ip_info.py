# ip_info.py
# Gets location and ISP info for an IP address using the free ipapi.co API.

import requests

URL = "https://ipapi.co/{}/json/"


def _na_dict():
    # make a new dict every time so nobody edits a shared one by accident
    return {
        "city": "N/A",
        "region": "N/A",
        "country": "N/A",
        "isp": "N/A",
        "asn": "N/A",
    }


def _get_value(data, field):
    # the API sometimes skips a field or sends null / "", so fall back to N/A
    value = data.get(field)
    if value is None or str(value).strip() == "":
        return "N/A"
    return str(value).strip()


def get_metadata(ip):
    # no IP = nothing to look up, and the free API has a request limit
    # so we don't waste a call
    if not ip or not str(ip).strip():
        return _na_dict()

    try:
        response = requests.get(URL.format(ip), timeout=5)

        # 429 means we got rate limited. Anything that isn't 200 counts as failed.
        if response.status_code != 200:
            return _na_dict()

        data = response.json()

        # ipapi can reply 200 and still put "error": true in the body
        if not isinstance(data, dict) or data.get("error"):
            return _na_dict()

        # ipapi's field names are different from ours (country_name, org)
        return {
            "city": _get_value(data, "city"),
            "region": _get_value(data, "region"),
            "country": _get_value(data, "country_name"),
            "isp": _get_value(data, "org"),
            "asn": _get_value(data, "asn"),
        }

    except Exception:
        # timeout, no internet, bad JSON, whatever. The main program shouldn't
        # crash because of this file, so every error just becomes N/A.
        return _na_dict()
