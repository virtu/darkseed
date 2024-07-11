"""Module for network addresses, including encoding/decoding of darknet addresses."""

import base64
import hashlib
from dataclasses import dataclass

from .address import Address
from .network import DarknetSpecs


@dataclass(frozen=True)
class AddressCodec:
    """
    Address Codec for encoding/decoding darknet addresses.

    Supported formats:
    - address
    - binary (corresponding to 256-bit pubkey (cjdns) or hash (i2p))
    - base64
    - base85
    """

    @staticmethod
    def encode_address(address: Address, encoding: str = "address") -> str | bytes:
        """Encoding address using encoding."""
        if encoding == "address":
            return address.address
        if not (address.onion or address.i2p):
            raise ValueError(f"Invalid encoding for network type: {address.net_type}")
        if address.onion:
            return OnionAddressCodec.encode_address(address, encoding)
        if address.i2p:
            return I2PAddressCodec.encode_address(address, encoding)
        raise ValueError(f"Unsupported network type: {address.net_type}")


class OnionAddressCodec:
    """Class for encoding/decoding Onion v3 addresses."""

    @staticmethod
    def encode_address(address: Address, encoding: str) -> str | bytes:
        """Encode Onion v3 address using specified encoding. Strip padding ("=") from base64/85"""
        pubkey = OnionAddressCodec.get_pubkey(address.address)
        if encoding == "base64":
            return base64.b64encode(pubkey).decode().rstrip("=")
        if encoding == "base85":
            return base64.b85encode(pubkey).decode().rstrip("=")
        if encoding == "raw":
            return pubkey
        if encoding == "raw_hex":
            return pubkey.hex()
        raise ValueError(f"Unsupported encoding: {encoding}")

    @staticmethod
    def get_pubkey(address: str) -> bytes:
        """Derive 256-bit public key from address.

        Ensure address ends with ".onion" then strip the suffix. Onion v3
        addresses are always 56 bytes, which is a multiple of 8, so no padding
        is required before decoding. Validate address version and checksum
        after decoding.
        """
        addr_encoded = address[: -len(DarknetSpecs.ONION_V3_ADDR_SUFFIX)]
        if len(addr_encoded) != DarknetSpecs.ONION_V3_ADDR_LEN:
            raise ValueError(f"Invalid Onion v3 address length: {addr_encoded}")
        decoded = base64.b32decode(addr_encoded.upper())
        pubkey = decoded[:32]
        version = decoded[34]
        checksum = decoded[32:34]
        OnionAddressCodec.validate_checksum(pubkey, checksum)
        if version != 3:
            raise ValueError(f"Invalid Onion v3 address version: {version}")
        return pubkey

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


class I2PAddressCodec:
    """Class for encoding/decoding I2P addresses."""

    @staticmethod
    def encode_address(address: Address, encoding: str) -> str | bytes:
        """Encode I2P address using specified encoding. Strip padding ("=") from base64/85."""
        hash_ = I2PAddressCodec.get_hash(address.address)
        if encoding == "base64":
            return base64.b64encode(hash_).decode().rstrip("=")
        if encoding == "base85":
            return base64.b85encode(hash_).decode().rstrip("=")
        if encoding == "raw":
            return hash_
        if encoding == "raw_hex":
            return hash_.hex()
        raise ValueError(f"Unsupported encoding: {encoding}")

    @staticmethod
    def get_hash(address: str) -> bytes:
        """Derive 256-bit hash from address.

        Ensure address ends with ".b32.i2p", then strip the suffix.
        Base32-encoding must be a multiple of eight: since the suffix-stripped
        address is always 52 bytes, four bytes of padding are added before
        decoding.
        """
        addr_encoded = address[: -len(DarknetSpecs.I2P_ADDR_SUFFIX)]
        if len(addr_encoded) != DarknetSpecs.I2P_ADDR_LEN:
            raise ValueError(f"Invalid I2P address length: {addr_encoded}")
        return base64.b32decode(addr_encoded.upper() + "====")
