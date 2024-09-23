"""Module for custom Darknet address encoding."""

import io
import ipaddress
import logging as log
from dataclasses import dataclass
from typing import ClassVar, List, Literal

import dns.rdata
import dns.rdatatype
import dns.rrset
from dns.rdataclass import IN
from dns.rdatatype import NULL as NULL_TYPE
from dns.rdtypes.IN.AAAA import AAAA

from darkseed.address import Address, BIP155Like


@dataclass
class AAAACodec:
    """Class representing custom AAAA records to encode arbitrary binary data.

    The encoding uses the following format:
    1. The IPv6 address in the AAAA record starts with the ff00::/8	prefix
    2. The next five bits of the address are interpreted as order

    """

    PREFIX: ClassVar[ipaddress.IPv6Network] = ipaddress.IPv6Network("ff00::/8")
    TOTAL_BITS: ClassVar[int] = PREFIX.max_prefixlen
    PREFIX_BITS: ClassVar[int] = PREFIX.prefixlen
    ORDER_BITS: ClassVar[int] = 5
    ORDER_START: ClassVar[int] = PREFIX_BITS
    ORDER_END: ClassVar[int] = PREFIX_BITS + ORDER_BITS
    PAYLOAD_START: ClassVar[int] = ORDER_END
    ENDIANNESS: ClassVar[Literal["big", "little"]] = "big"

    @staticmethod
    def decode(records: List[AAAA]) -> List[Address]:
        """Decode addesses in binary data from a list of dnspython AAAA records.

        First, find all AAAA records with the codec's prefix. Next, extract the
        IPv6 addresses from the records and order them based on data in the
        order bits. Finally, extract the data bits from the ordered addresses and
        concatenate them to form the binary data.
        """
        data = [
            bin(int(ipaddress.IPv6Address(r.address)))[2:].zfill(AAAACodec.TOTAL_BITS)
            for r in records
            if ipaddress.IPv6Address(r.address) in AAAACodec.PREFIX
        ]
        ordered_data = sorted(
            data, key=lambda x: int(x[AAAACodec.ORDER_START : AAAACodec.ORDER_END], 2)
        )
        payload_bin = "".join(d[AAAACodec.PAYLOAD_START :] for d in ordered_data)
        payload_bytes = int(payload_bin, 2).to_bytes(
            (len(payload_bin) + 7) // 8, byteorder=AAAACodec.ENDIANNESS
        )

        # Figure out length necessary? just call BIP155Like.decode?
        s = io.BytesIO(payload_bytes)
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
class AAAARecord:
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
