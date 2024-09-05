"""Module for network addresses, including encoding/decoding of darknet addresses."""

from dataclasses import dataclass
from functools import cached_property

from .network import NetworkType


@dataclass
class Address:
    """Class representing network addresses."""

    address: str

    def __str__(self) -> str:
        """Include network type in string representation."""
        return f"Address(addr={self.address}, net_type={self.net_type})"

    @cached_property
    def net_type(self) -> NetworkType:
        """Determine network type based on address string."""
        return NetworkType.get_type(self.address)

    @cached_property
    def ipv4(self) -> bool:
        """Check if address is an IPv4 address."""
        return NetworkType.is_ipv4(self.address)

    @cached_property
    def ipv6(self) -> bool:
        """Check if address is an IPv6 address."""
        return NetworkType.is_ipv6(self.address)

    @cached_property
    def cjdns(self) -> bool:
        """Check if address is a cjdns address."""
        return NetworkType.is_cjdns(self.address)

    @cached_property
    def i2p(self) -> bool:
        """Check if address is an I2P address."""
        return NetworkType.is_i2p(self.address)

    @cached_property
    def onion(self) -> bool:
        """Check if address is an onion address."""
        return NetworkType.is_onion(self.address)
