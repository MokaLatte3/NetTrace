from rich.console import Console
from rich.table import Table

def show(ipv4, ipv6, metadata):
    console = Console()

    table = Table(title="NetTrace - IP Addresses", show_header=True, header_style="bold cyan")

    table.add_column("Property", style="bold")
    table.add_column("Value")

    if ipv4 is None:
        ipv4 = "[yellow]Not Available[/yellow]"

    if ipv6 is None:
        ipv6 = "[yellow]Not Available[/yellow]"

    table.add_row("IPv4 Address", str(ipv4))
    table.add_row("IPv6 Address", str(ipv6))

    if metadata is None:
        metadata = {}

    table.add_row("City", str(metadata.get("city", "[yellow]Not Available[/yellow]")))
    table.add_row("Region", str(metadata.get("region", "[yellow]Not Available[/yellow]")))
    table.add_row("Country", str(metadata.get("country", "[yellow]Not Available[/yellow]")))
    table.add_row("ISP", str(metadata.get("isp", "[yellow]Not Available[/yellow]")))
    table.add_row("ASN", str(metadata.get("asn", "[yellow]Not Available[/yellow]")))

    console.print(table)