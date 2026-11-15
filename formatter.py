from rich.console import Console
from rich.table import Table

def show(ipv4, ipv6, metadata):
    # Initializing the terminal console to create a structured table
    # presenting the retrieved IP Addresses and metadata
    console = Console()

    table = Table(title="NetTrace - IP Addresses", show_header=True, header_style="bold cyan")

    # Separating network properties from their respective values
    # for better readability.
    table.add_column("Property", style="bold")
    table.add_column("Value")

    # Handling missing IP Addresses to clearly indicate
    # missing information in the output
    if ipv4 is None:
        ipv4 = "[yellow]N/A[/yellow]"

    if ipv6 is None:
        ipv6 = "[yellow]N/A[/yellow]"

    # Add detected IP Addresses to the table
    table.add_row("IPv4 Address", str(ipv4))
    table.add_row("IPv6 Address", str(ipv6))

    # Uses an empty dictionary if no metadata is provided
    # to prevent errors when accessing individual fields
    if metadata is None:
        metadata = {}

    # Retrieve individual metadata field with a default value
    # of Not Available to catch missing fields without interruption
    table.add_row("City", str(metadata.get("city", "[yellow]N/A[/yellow]")))
    table.add_row("Region", str(metadata.get("region", "[yellow]N/A[/yellow]")))
    table.add_row("Country", str(metadata.get("country", "[yellow]N/A[/yellow]")))
    table.add_row("ISP", str(metadata.get("isp", "[yellow]N/A[/yellow]")))
    table.add_row("ASN", str(metadata.get("asn", "[yellow]N/A[/yellow]")))

    # Display the completed table in the terminal
    console.print(table)
