# NetTrace

NetTrace is a Python command-line tool that shows your computer's **public IPv4 and IPv6 addresses**, along with information about that address: **city, region, country, ISP, and ASN**. It was built as a prototype for network technicians for DEVASC Project Activity 3.

## What it does

When you run NetTrace, it:

1. Gets your public IPv4 and IPv6 addresses from the [ipify](https://www.ipify.org/) API
2. Looks up the location and network details of that address from the [ipapi.co](https://ipapi.co/) API
3. Shows everything in a formatted table in the terminal

If something fails (no IPv6 on your network, no internet, a timeout, or the API rate-limiting you), NetTrace does **not** crash. It shows `N/A` for anything it couldn't get.

## Requirements

- Python 3.10 or newer
- Internet connection (for real lookups; the tests run offline)

## Setup

Clone the repo and create a virtual environment:

```bash
git clone https://github.com/MokaLatte3/NetTrace.git
cd NetTrace
python -m venv .venv
```

Activate it:

```bash
# Windows (PowerShell)
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

> If PowerShell says "running scripts is disabled", run
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then activate again.

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python nettrace.py          # show your public IP info
python nettrace.py --help   # show usage
```

Example output:

```
          NetTrace - IP Addresses
┌──────────────┬──────────────────┐
│ Property     │ Value            │
├──────────────┼──────────────────┤
│ IPv4 Address │ 203.0.113.5      │
│ IPv6 Address │ N/A              │
│ City         │ Manila           │
│ Region       │ Metro Manila     │
│ Country      │ Philippines      │
│ ISP          │ Example Telecom  │
│ ASN          │ AS0000           │
└──────────────┴──────────────────┘
```

### Exit codes

| Code | Meaning |
|---|---|
| `0` | At least one public IP address was found |
| `1` | No IP address was found (e.g. no internet) |

This lets other scripts check if NetTrace worked:

```powershell
python nettrace.py
echo $LASTEXITCODE
```

## Project structure

| File | What it does |
|---|---|
| `nettrace.py` | Main program. Handles `--help`, calls the other modules in order, and returns the exit code |
| `detection.py` | Gets the public IPv4/IPv6 address from ipify and checks it's a valid address |
| `ip_info.py` | Gets city, region, country, ISP, and ASN from ipapi.co |
| `formatter.py` | Displays the results in a table using the `rich` library |
| `tests/` | Unit tests for each module, plus an integration test |
| `requirements.txt` | Python packages needed (`requests`, `rich`) |

## How the modules fit together (the contract)

Before coding, we agreed on the exact functions each module provides, so everyone could work at the same time:

```python
detection.get_public_ip(version) -> str | None
    # version is 4 or 6
    # returns the IP as a string, or None if it can't be found (never raises)

ip_info.get_metadata(ip) -> dict
    # returns {"city", "region", "country", "isp", "asn"}
    # any missing value or API failure becomes "N/A" (never raises)

formatter.show(ipv4, ipv6, metadata) -> None
    # prints the table; None or missing values are shown as "N/A"

nettrace.main(argv=None) -> int
    # runs the whole program and returns the exit code (0 or 1)
```

Flow:

```
nettrace.py ──► detection.py   (ipify)     → IPv4 / IPv6
            ──► ip_info.py     (ipapi.co)  → city, region, country, ISP, ASN
            ──► formatter.py               → table in the terminal
```

If no IPv4 address is found, `nettrace.py` uses the IPv6 address for the metadata lookup. If neither is found, it skips the lookup entirely.

## Running the tests

```bash
python -m unittest discover -v
```

All API calls in the tests are **mocked** (faked), so the tests run without internet and don't use up the API's free limit.

- **Unit tests** check each module on its own.
- **Integration test** (`tests/test_integration.py`) runs the real `detection`, `ip_info`, and `formatter` together, faking only the internet.

## Known limitations

- **ipapi.co rate limits:** the free plan limits how many requests can come from one IP address. On shared networks (like mobile data, where many users share one public IP), the limit can be reached by other people, and the location fields will show `N/A`. The app still works and finds your IP.
- **IPv6:** many networks don't support IPv6, so the IPv6 row will often show `N/A`. This is expected.

## Future enhancements (backlog)

| Enhancement | Why |
|---|---|
| Fallback API (e.g. ip-api.com) when ipapi.co rate-limits | We hit ipapi.co's limit during testing; ip-api.com was confirmed to work on our network |
| `--target <IP>` option | Let technicians look up any IP, not just their own |
| `--json` output | Let other scripts use NetTrace's results |
| Run tests automatically with GitHub Actions | Catch failing tests before they're merged |
| Cache the last successful lookup | Avoid calling the API on every run and reduce rate-limit problems |

## How to continue the project

1. Follow **Setup** above and run the tests to make sure everything passes.
2. Pick a module to change. As long as it still follows the **contract** above, the other modules keep working without changes.
3. Add or update tests for your change in `tests/`.
4. Create a branch, open a pull request into `main`, and have another member review it before merging.