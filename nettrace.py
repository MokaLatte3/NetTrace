import argparse
import sys

import detection
import ip_info
import formatter


def build_parser():
    parser = argparse.ArgumentParser(
        prog="nettrace",
        description="A simple tool to output your public IP addresses and location information.",  #Description shown in --help
    )
    return parser


def main(argv=None):
    parser = build_parser()
    parser.parse_args(argv)

    ipv4 = detection.get_public_ip(4)
    ipv6 = detection.get_public_ip(6)

    # only lookup for metadata if we find an IP, otherwise skip the call and output N/A
    lookup_ip = ipv4 or ipv6
    if lookup_ip:
        info = ip_info.get_metadata(lookup_ip)
    else:
        info = None

    formatter.show(ipv4, ipv6, info)

    # 0 if either v4 or v6 IP is found, 1 if neither
    if ipv4 or ipv6:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())