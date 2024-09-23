"""Module for custom Darknet address encoding."""

import io
import ipaddress
import logging as log
from dataclasses import dataclass
from typing import ClassVar, List, Literal

import dns.rdata
import dns.rrset
from dns.rdataclass import IN
from dns.rdatatype import AAAA as AAAA_TYPE
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
    PREFIX_BYTES: ClassVar[int] = 1
    ORDER_BYTES: ClassVar[int] = 1
    ENDIANNESS: ClassVar[Literal["big", "little"]] = "big"
    PAYLOAD_BYTES = 14  # 14B (16B total less 1B PREFIX and 1B ORDER)
    RECORD_LIMIT = (
        17  # 512B DNS message limit less 12B header / 28B per record -> max. 17 records
    )

    @staticmethod
    def decode(records: List[AAAA]) -> List[Address]:
        """Decode addresses in binary data from a list of dnspython AAAA records.

        First, find all AAAA records with the codec's prefix. Next, extract the
        IPv6 addresses from the records and order them based on data in the
        order bits. Finally, extract the data bits from the ordered addresses and
        concatenate them to form the binary data.
        """

        pos_to_payload = {}
        for record in records:
            if not isinstance(record, AAAA):
                log.debug("Skipping non-AAAA record: %s", record)
            if ipaddress.IPv6Address(record.address) not in AAAACodec.PREFIX:
                log.debug("Skipping AAAA record not matching prefix: %s", record)
            log.debug("Processing AAAA record: %s", record)
            address = ipaddress.IPv6Address(record.address)
            pos = address.packed[1]
            payload = address.packed[2:]
            pos_to_payload[pos] = payload
            log.debug("Extracted pos: %d, payload: %s", pos, payload)

        full_payload = b"".join(pos_to_payload[p] for p in range(len(pos_to_payload)))
        log.debug("Full payload: %s", full_payload)

        log.debug("Attempting to decode addresses...")
        s = io.BytesIO(full_payload)
        num_records = int.from_bytes(s.read(1), "big")
        addresses = []
        for _ in range(num_records):
            address = BIP155Like.decode(s)
            addresses.append(address)
        log.debug(
            "Extracted %d addresses from %d custom AAAA records",
            len(addresses),
            len(pos_to_payload),
        )
        return addresses

    @staticmethod
    def encode(addresses: List[Address]) -> List[AAAA]:
        """Encode addresses using custom AAAA records."""

        if len(addresses) == 0:
            raise ValueError("No addresses to encode")
        data = b"".join(BIP155Like.encode(addr) for addr in addresses)
        s = io.BytesIO(data)
        records = []
        for pos in range(AAAACodec.RECORD_LIMIT):
            payload = s.read(AAAACodec.PAYLOAD_BYTES)
            if not payload:
                break
            if len(payload) < AAAACodec.PAYLOAD_BYTES:
                payload += b"\x00" * (AAAACodec.PAYLOAD_BYTES - len(payload))
            ip = ipaddress.IPv6Address(b"\xff" + pos.to_bytes(1, "big") + payload)
            log.debug("Encoding payload %s into address %s", payload, ip)
            log.debug("ip={ip}, str(ip)={str(ip)}")
            record = AAAA(IN, AAAA_TYPE, str(ip))
            records.append(record)
            pos += 1
        if s.tell() != len(data):
            raise ValueError("Could not encode all data!")
        log.debug(
            "Encoded %d addresses into %d AAAA records",
            len(addresses),
            len(records),
        )
        return records


@dataclass
class CustomAAAARecords:
    """Class for encoding via custom AAAA records."""

    @staticmethod
    def build_records(
        addresses: List[Address], domain: str, ttl: int = 60
    ) -> List[dns.rrset.RRset]:
        """Create custom AAAA records for addresses."""
        for address in addresses:
            if address.ipv4 or address.ipv6:
                raise ValueError(f"Unsupported address type: {address.net_type}")

        list_rdata = AAAACodec.encode(addresses)
        records = [dns.rrset.from_rdata(domain, ttl, rdata) for rdata in list_rdata]
        return records
