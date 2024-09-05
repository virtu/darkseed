"""BIP155-like address encoding and decoding."""

import base64
import hashlib
import io
import ipaddress
from dataclasses import dataclass
from typing import ClassVar

from .address import Address
from .network import DarknetSpecs


@dataclass
class NetworkConf:
    """Class representing network configuration parameters."""

    net_id: int
    address_len: int


@dataclass
class BIP155:
    """BIP155 network parameters."""

    IPV4: ClassVar[NetworkConf] = NetworkConf(0x01, 4)
    IPV6: ClassVar[NetworkConf] = NetworkConf(0x02, 16)
    TORV2: ClassVar[NetworkConf] = NetworkConf(0x03, 10)
    TORV3: ClassVar[NetworkConf] = NetworkConf(0x04, 32)
    I2P: ClassVar[NetworkConf] = NetworkConf(0x05, 32)
    CJDNS: ClassVar[NetworkConf] = NetworkConf(0x06, 16)
    YGGDRASIL: ClassVar[NetworkConf] = NetworkConf(0x07, 16)


@dataclass(frozen=True)
class BIP155Like:
    """
    BIP155-Like Codec for encoding/decoding darknet addresses. Does not include
    a timestamp or port as BIP155.
    """

    @staticmethod
    def encode(address: Address) -> bytes:
        """Encode address using encoding."""
        if not (address.onion or address.i2p or address.cjdns):
            raise ValueError(f"Invalid encoding for network type: {address.net_type}")
        if address.onion:
            net_id_bytes = BIP155.TORV3.net_id.to_bytes(1, "big")
            data = OnionAddressCodec.encode_address(address, encoding="raw")
            assert isinstance(data, bytes)
            return net_id_bytes + data
        if address.i2p:
            net_id_bytes = BIP155.I2P.net_id.to_bytes(1, "big")
            data = I2PAddressCodec.encode_address(address, encoding="raw")
            assert isinstance(data, bytes)
            return net_id_bytes + data
        if address.cjdns:
            net_id_bytes = BIP155.CJDNS.net_id.to_bytes(1, "big")
            data = ipaddress.ip_address(address.address).packed
            return net_id_bytes + data
        raise ValueError(f"Unsupported network type: {address.net_type}")

    @staticmethod
    def _supported_networks(net_id: int) -> bool:
        """Check if network is supported."""
        return net_id in (BIP155.TORV3.net_id, BIP155.I2P.net_id, BIP155.CJDNS.net_id)

    @staticmethod
    def decode(s: io.BytesIO) -> Address:
        """Encode address using encoding."""
        net_id = int.from_bytes(s.read(1), "big")
        if net_id == BIP155.TORV3.net_id:
            address_len = BIP155.TORV3.address_len
            decoder = OnionAddressCodec.pubkey_to_address
        elif net_id == BIP155.I2P.net_id:
            address_len = BIP155.I2P.address_len
            decoder = I2PAddressCodec.hash_to_address
        elif net_id == BIP155.CJDNS.net_id:
            address_len = BIP155.CJDNS.address_len

            def decoder_(data):
                return str(ipaddress.ip_address(data))

            decoder = decoder_
        else:
            raise ValueError(f"Unsupported network id: {net_id}")
        address_data = s.read(address_len)
        address_str = decoder(address_data)
        return Address(address_str)


class OnionAddressCodec:
    """Class for encoding/decoding Onion v3 addresses."""

    @staticmethod
    def pubkey_to_address(pubkey: bytes) -> str:
        """Convert 256-bit public key to Onion v3 address."""
        version = b"\x03"
        checksum = OnionAddressCodec.compute_checksum(pubkey)
        return (
            base64.b32encode(pubkey + checksum + version).decode().rstrip("=").lower()
            + DarknetSpecs.ONION_V3_ADDR_SUFFIX
        )

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
        checksum_expected = decoded[32:34]
        checksum_computed = OnionAddressCodec.compute_checksum(pubkey)
        if checksum_computed != checksum_expected:
            raise ValueError(
                f"Invalid Onion v3 address checksum: "
                f"expected={checksum_expected}, computed={checksum_computed}"
            )
        if version != 3:
            raise ValueError(f"Invalid Onion v3 address version: {version}")
        return pubkey

    @staticmethod
    def compute_checksum(pubkey: bytes) -> bytes:
        """Compute checksum for public key.

        To compute checksum, concatenate ".onion checksum" with pubkey and
        version (3); then hash with sha256 and use the first two bytes.
        """
        checksum_input = b".onion checksum" + pubkey + b"\x03"
        return hashlib.sha3_256(checksum_input).digest()[:2]


class I2PAddressCodec:
    """Class for encoding/decoding I2P addresses."""

    @staticmethod
    def hash_to_address(pubkey: bytes) -> str:
        """Convert 256-bit hash to I2P address."""
        return (
            base64.b32encode(pubkey).decode().rstrip("=").lower()
            + DarknetSpecs.I2P_ADDR_SUFFIX
        )

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
