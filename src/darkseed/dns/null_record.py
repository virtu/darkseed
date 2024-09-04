"""Module for custom Darknet address encoding."""

import io
import logging as log
from dataclasses import dataclass
from typing import List

import dns.rdata
import dns.rrset
from dns.rdataclass import IN
from dns.rdatatype import NULL as NULL_TYPE

from darkseed.address import Address, BIP155Like


@dataclass
class NullRecordCodec:
    """Class representing custom NULL records.

    Format: <num_records> <record_1> ... <record_n>,
    where <record_n> is <bip155_type> <bip155_encoded_addresses>
    """

    @staticmethod
    def decode(data: bytes) -> List[Address]:
        """Extract addresses from NullRecord."""
        s = io.BytesIO(data)
        num_records = int.from_bytes(s.read(1), "big")
        addresses = []
        for _ in range(num_records):
            address = BIP155Like.decode(s)
            addresses.append(address)
        log.debug(
            "Extracted %d addresses from NullRecord (size=%d, records=%d)",
            len(addresses),
            len(data),
            num_records,
        )
        return addresses

    @staticmethod
    def encode(addresses: List[Address]) -> bytes:
        """Encode addresses into NullRecord."""
        s = io.BytesIO()
        num_records = len(addresses)
        s.write(num_records.to_bytes(1, "big"))
        for address in addresses:
            data = BIP155Like.encode(address)
            s.write(data)
        data = s.getvalue()
        log.debug(
            "Encoded %d addresses into NullRecord (size=%d)",
            len(addresses),
            len(data),
        )
        return data


@dataclass
class NullRecord:
    """Class representing a DNS NULL record."""

    @staticmethod
    def build_record(
        addresses: list[Address], domain: str, ttl: int = 60
    ) -> dns.rrset.RRset:
        """Encode multiple addresses into a single DNS NULL record."""
        num_records = len(addresses)
        if num_records == 0 or num_records > 255:
            raise ValueError(f"Invalid number of records: {num_records}")
        null_record = NullRecordCodec.encode(addresses)
        rdata = dns.rdata.from_wire(IN, NULL_TYPE, null_record, 0, len(null_record))
        record = dns.rrset.from_rdata(domain, ttl, rdata)
        return record
