"""Module for network classes."""

import ipaddress
from dataclasses import dataclass
from enum import Enum, auto


@dataclass(frozen=True)
class DarknetSpecs:
    """Network address suffixes used by darknet protocols."""

    CJDNS_ADDR_PREFIX = "fc"
    I2P_ADDR_LEN = 52
    I2P_ADDR_SUFFIX = ".b32.i2p"
    ONION_V3_ADDR_SUFFIX = ".onion"
    ONION_V3_ADDR_LEN = 56


class NetworkType(Enum):
    """Class representing network types."""

    IPV4 = auto()
    IPV6 = auto()
    ONION_V3 = auto()
    I2P = auto()
    CJDNS = auto()

    def __str__(self) -> str:
        """Return a lower-case string representation of the enum member."""
        return self.name.lower()

    @staticmethod
    def get_type(address: str) -> "NetworkType":
        """Derive network type from address string."""
        if address.endswith(DarknetSpecs.I2P_ADDR_SUFFIX):
            return NetworkType.I2P
        if address.endswith(DarknetSpecs.ONION_V3_ADDR_SUFFIX):
            return NetworkType.ONION_V3
        try:
            ip = ipaddress.ip_address(address)
            if ip.version == 4:
                return NetworkType.IPV4
            if address.lower().startswith(DarknetSpecs.CJDNS_ADDR_PREFIX):
                return NetworkType.CJDNS
            return NetworkType.IPV6
        except ValueError as e:
            raise ValueError(f"Unsupported address type: {address}") from e

    @staticmethod
    def is_ipv4(address: str) -> bool:
        """Check if address is an IPv4 address."""
        return NetworkType.get_type(address) == NetworkType.IPV4

    @staticmethod
    def is_ipv6(address: str) -> bool:
        """Check if address is an IPv6 address."""
        return NetworkType.get_type(address) == NetworkType.IPV6

    @staticmethod
    def is_cjdns(address: str) -> bool:
        """Check if address is a cjdns address."""
        return NetworkType.get_type(address) == NetworkType.CJDNS

    @staticmethod
    def is_i2p(address: str) -> bool:
        """Check if address is an I2P address."""
        return NetworkType.get_type(address) == NetworkType.I2P

    @staticmethod
    def is_onion(address: str) -> bool:
        """Check if address is an onion address."""
        return NetworkType.get_type(address) == NetworkType.ONION_V3
