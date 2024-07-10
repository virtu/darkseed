"""Module for network addresses, including encoding/decoding of darknet addresses."""

import base64
import hashlib
import ipaddress
from dataclasses import dataclass
from functools import cached_property
from typing import ClassVar


@dataclass
class Address:
    """
    Generic address class.

    Instantiates dedicated classes for Onion and I2P addresses which provide
    functionality for encoding/decoding.
    """

    address: str

    def __new__(cls, address: str):
        network = Address.get_network(address)
        if cls is Address:
            if network == "i2p":
                return I2PAddress(address)
            if network == "onion_v3":
                return OnionV3Address(address)
        return super(Address, cls).__new__(cls)

    def __post_init__(self):
        """Set network type."""
        self.network = self.get_network(self.address)

    @staticmethod
    def get_network(address: str) -> str:
        """Determine network type based on address format."""
        if address.endswith(I2PAddress.SUFFIX):
            return "i2p"
        if address.endswith(OnionV3Address.SUFFIX):
            return "onion_v3"
        try:
            ip = ipaddress.ip_address(address)
        except ValueError as e:
            raise ValueError(f"Unsupported address type: {address}") from e
        if ip.version == 4:
            return "ipv4"
        if ip.version == 6 and address.lower().startswith("fc"):
            return "cjdns"
        return "ipv6"


@dataclass
class I2PAddress(Address):
    """Class for I2P addresses."""

    SUFFIX: ClassVar[str] = ".b32.i2p"

    @cached_property
    def hash(self) -> bytes:
        """Derive 256-bit hash from address.

        Ensure address ends with ".b32.i2p", then strip the suffix.
        Base32-encoding must be a multiple of eight: since the suffix-stripped
        address is always 52 bytes, four bytes of padding are added before
        decoding.
        """
        if not self.address.endswith(I2PAddress.SUFFIX):
            raise ValueError(f"Invalid I2P address suffix: {self.address}")
        addr_encoded = self.address[: -len(I2PAddress.SUFFIX)]
        if len(addr_encoded) != 52:
            raise ValueError(f"Invalid I2P address length: {addr_encoded}")
        return base64.b32decode(addr_encoded.upper() + "====")

    @cached_property
    def bytes_raw(self) -> bytes:
        """Get byte data."""
        return self.hash

    @cached_property
    def bytes_hex(self) -> str:
        """Get hex-encoded byte data."""
        return self.hash.hex()

    @cached_property
    def base64(self) -> str:
        """Convert 256-bit hash to base64."""
        return base64.b64encode(self.hash).decode()

    @cached_property
    def base85(self) -> str:
        """Convert 256-bit hash to base85."""
        return base64.b85encode(self.hash).decode()


@dataclass
class OnionV3Address(Address):
    """Class for Onion v3 addresses."""

    SUFFIX: ClassVar[str] = ".onion"

    @staticmethod
    def validate_checksum(pubkey: bytes, checksum_expected: bytes):
        """Compute and validate checksum for public key.

        To compute checksum, concatenate ".onion checksum" with pubkey and
        version (3); then hash with sha256 and use the first two bytes.
        """
        checksum_input = b".onion checksum" + pubkey + b"\x03"
        checksum_computed = hashlib.sha3_256(checksum_input).digest()[:2]
        if checksum_computed != checksum_expected:
            raise ValueError(
                f"Invalid Onion v3 address checksum: "
                f"expected={checksum_expected}, computed={checksum_computed}"
            )

    @cached_property
    def pubkey(self) -> bytes:
        """Derive 256-bit public key from address.

        Ensure address ends with ".onion" then strip the suffix. Onion v3
        addresses are always 56 bytes, which is a multiple of 8, so no padding
        is required before decoding. Validate address version and checksum
        after decoding.
        """
        if not self.address.endswith(OnionV3Address.SUFFIX):
            raise ValueError(f"Invalid Onion v3 address suffix: {self.address}")
        addr_encoded = self.address[: -len(OnionV3Address.SUFFIX)]
        if len(addr_encoded) != 56:
            raise ValueError(f"Invalid Onion v3 address length: {addr_encoded}")
        decoded = base64.b32decode(addr_encoded.upper())
        pubkey = decoded[:32]
        version = decoded[34]
        checksum = decoded[32:34]
        OnionV3Address.validate_checksum(pubkey, checksum)
        if version != 3:
            raise ValueError(f"Invalid Onion v3 address version: {version}")
        return pubkey

    @cached_property
    def bytes_raw(self) -> bytes:
        """Get byte data."""
        return self.pubkey

    @cached_property
    def bytes_hex(self) -> str:
        """Get hex-encoded byte data."""
        return self.pubkey.hex()

    @cached_property
    def base64(self) -> str:
        """Convert 256-bit pubkey to base64."""
        return base64.b64encode(self.pubkey).decode()

    @cached_property
    def base85(self) -> str:
        """Convert 256-bit pubkey to base85."""
        return base64.b85encode(self.pubkey).decode()
