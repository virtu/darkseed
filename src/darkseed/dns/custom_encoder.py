"""Module for custom Darknet address encoding."""

import logging as log
from dataclasses import dataclass
from typing import ClassVar, List

import dns.rdata
import dns.rrset
from dns.rdataclass import IN
from dns.rdatatype import NULL as NULL_TYPE

from darkseed.node import (Address, AddressCodec, I2PAddressCodec,
                           OnionAddressCodec)


@dataclass
class CustomNullEncoding:
    """Class representing data used in custom NULL records."""

    num_records: int
    records: List["CustomNullEncodingRecord"]

    @classmethod
    def from_bytes(cls, data: bytes) -> "CustomNullEncoding":
        """Create a CustomNullEncoding instance from bytes."""
        num_records = int.from_bytes([data[0]], "big")
        records = []
        pos = 1
        for _ in range(num_records):
            record = CustomNullEncodingRecord.from_bytes(
                data[pos : pos + CustomNullEncodingRecord.RECORD_LEN]
            )
            records.append(record)
            pos += CustomNullEncodingRecord.RECORD_LEN
        return cls(num_records, records)


@dataclass
class CustomNullEncodingRecord:
    """Class representing a record used in CustomNullEncoding."""

    type: int
    data: bytes
    _address: str

    def __str__(self):
        """Include original address in string representations."""
        return f"Record(type={self.type}, data={self.data.hex()}) was={self._address}"

    ONION_V3_ADDR: ClassVar[int] = 0
    I2P_ADDR: ClassVar[int] = 1 << 0
    RECORD_LEN: ClassVar[int] = 1 + 32  # 1-byte type + 32-byte data

    def to_wire(self) -> bytes:
        """Convert into wire format (bytes)."""
        return self.type.to_bytes(1, "big") + self.data

    @classmethod
    def from_bytes(cls, data: bytes) -> "CustomNullEncodingRecord":
        """Create a CustomNullEncodingRecord instance from bytes."""
        if len(data) != CustomNullEncodingRecord.RECORD_LEN:
            raise ValueError(f"Invalid record length: {len(data)}")
        record_type = int.from_bytes([data[0]])
        if record_type not in (cls.ONION_V3_ADDR, cls.I2P_ADDR):
            raise ValueError(f"Invalid record type: {record_type}")
        record_data = data[1:]
        if record_type == cls.ONION_V3_ADDR:
            # TODO
            # Address class that instantiates appropriate subclasses would be
            # better! Address.to_pubkey(), to_binary(), to_base64(), etc.;
            # maybe make it Address.from_str() Address.from_bytes() as well!
            address = OnionAddressCodec.pubkey_to_address(record_data)
            return cls(record_type, record_data, address)
        if record_type == cls.I2P_ADDR:
            address = I2PAddressCodec.hash_to_address(record_data)
            return cls(record_type, record_data, address)
        raise ValueError(f"Invalid record type: {record_type}")

    @classmethod
    def from_address(cls, address: Address) -> "CustomNullEncodingRecord":
        """Create a CustomNullEncodingRecord instance from an Address."""
        record_type = CustomNullEncodingRecord.address_to_type(address)
        record_data = AddressCodec.encode_address(address, encoding="raw")
        assert isinstance(record_data, bytes), "Expected data to be bytes"
        return cls(record_type, record_data, address.address)

    @staticmethod
    def address_to_type(address: Address) -> int:
        """Detremine record type for address."""
        if address.onion:
            return CustomNullEncodingRecord.ONION_V3_ADDR
        if address.i2p:
            return CustomNullEncodingRecord.I2P_ADDR
        raise ValueError(f"Unsupported address type: {address}")


@dataclass(frozen=True)
class MultiAddressCodec:
    """
    Class for encoding and decoding multiple addresses in a single DNS NULL
    record using a custom binary format:

    <num_records> <record_1> ... <record_n>,
    where an individual <record> comprises:
        <type>: onion or i2p; and
        <data>: 256-bit pubkey or hash
    """

    @staticmethod
    def build_record(
        addresses: list[Address],
        domain: str = "seed.21.ninja.",
        ttl: int = 60,
    ) -> dns.rrset.RRset:
        """Encode multiple addresses into a single DNS NULL record."""
        num_records = len(addresses)
        assert 0 < num_records < 256, f"Invalid number of records: {num_records}"
        rdata = num_records.to_bytes(1, "big")
        log.debug("num_records=%d, rdata=%s", num_records, rdata.hex())
        for address in addresses:
            record = CustomNullEncodingRecord.from_address(address)
            rdata += record.to_wire()
            log.debug("Added new record %s, rdata=%s", record, rdata.hex())
        rdata = dns.rdata.from_wire(IN, NULL_TYPE, rdata, 0, len(rdata))
        record = dns.rrset.from_rdata(domain, ttl, rdata)
        return record
