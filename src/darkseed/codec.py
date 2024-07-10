"""Module for DNS records encoding and decoding functionality."""

from dnslib import AAAA, QTYPE, TXT, A

from darkseed.address import Address


class Codec:
    """DNS codec class."""

    @staticmethod
    def get_rtype(address: Address) -> int:
        """Get DNS resource record type."""
        if address.network == "ipv4":
            return QTYPE.A
        if address.network in ["ipv6", "cjdns"]:
            return QTYPE.AAAA
        if address.network in ["onion_v3", "i2p"]:
            return QTYPE.TXT
        raise ValueError(f"Unsupported network: {address.network}")

    @staticmethod
    def get_rdata(address: Address, fmt="address"):
        """Get DNS resource record data."""
        if address.network == "ipv4" and fmt == "address":
            return A(address.address)
        if address.network in ["ipv6", "cjdns"] and fmt == "address":
            return AAAA(address.address)
        if address.network in ["onion_v3", "i2p"]:
            try:
                data = getattr(address, fmt)
                return TXT(data)
            except AttributeError as e:
                raise ValueError(
                    f"Unsupported format {fmt} for {address.network}"
                ) from e
        raise ValueError(f"Unsupported format {fmt} for {address.network}")
