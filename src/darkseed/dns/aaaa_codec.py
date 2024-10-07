"""Module for custom Darknet address encoding."""

import io
import ipaddress
import logging as log
import random
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

    Addresses are serialized using a BIP155-like encoding (just the address
    type and data, so no timestamp and port). The serialized addresses are then
    concatenated, prefixed with the number of addresses, and broken into
    14-byte chunks. Each chunk is stored in a DNS AAAA record; in particular in
    bytes two through fourteen of the AAAA record's data field. To identify the
    custom encoding, the first byte of the data field is set to match the
    restricted IPv6 prefix ff00::/8. To deal with recursive DNS resolvers
    potentially reordering records, the second byte of the data field is used
    to store the ordering of the records.

    Decoding works in reverse: first, all AAAA records with the custom prefix
    are identified; next, the ordering is restored, the 14-byte payload chunks
    are extracted concatenated in the correct order; finally, the data can be
    decoded using the BIP155-like format.
    """

    PREFIX: ClassVar[ipaddress.IPv6Network] = ipaddress.IPv6Network("fc00::/8")
    RDATA_BYTES = 16  # 128-bit/16-byte IPv6 address
    PREFIX_BYTES: ClassVar[int] = 1
    ORDER_BYTES: ClassVar[int] = 1
    ENDIANNESS: ClassVar[Literal["big", "little"]] = "big"
    PAYLOAD_BYTES = RDATA_BYTES - PREFIX_BYTES - ORDER_BYTES
    # The record limit represents the maximum number of AAAA records that can
    # be included in the DNS reply without having it exceed the maximum size of
    # DNS messages, which is 512 bytes. The limit is calculated as follows:
    # floor(470 bytes / 28 bytes per record) = 16 records, where
    # 470B is given by 512B (max size) - 12B (header) - 30B (question); and
    # 28 B/record is given by 2B each for name pointer, type, class, and record
    # length as well as 4B for TTL and 16 bytes of actual data (IPv6 address)
    RECORD_LIMIT = 16

    @staticmethod
    def decode(records: List[dns.rrset.RRset]) -> List[Address]:
        """Decode addresses from list of DNS records."""
        pos_to_payload = {}
        for record in records:
            if not isinstance(record, AAAA):
                log.debug("Skipping non-AAAA record: %s", record)
                continue
            if ipaddress.IPv6Address(record.address) not in AAAACodec.PREFIX:
                log.debug("Skipping AAAA record not matching prefix: %s", record)
                continue
            log.debug("Processing AAAA record: %s", record)
            address = ipaddress.IPv6Address(record.address)
            pos = address.packed[1]
            payload = address.packed[2:]
            pos_to_payload[pos] = payload
            log.debug("Extracted pos=%d, payload=%s", pos, payload)
        full_payload = b"".join(pos_to_payload[p] for p in range(len(pos_to_payload)))
        log.debug("Attempting to decode full payload... (%s)", full_payload)
        s = io.BytesIO(full_payload)
        num_addrs = int.from_bytes(s.read(1), "big")
        addresses = []
        for _ in range(num_addrs):
            address = BIP155Like.decode(s)
            addresses.append(address)
        log.debug(
            "Extracted %d addresses from %d custom AAAA records",
            len(addresses),
            len(records),
        )
        return addresses

    @staticmethod
    def encode(
        addresses: List[Address], domain: str, ttl: int = 60
    ) -> List[dns.rrset.RRset]:
        """Encode addresses using custom AAAA record data."""
        if len(addresses) == 0:
            raise ValueError("No addresses to encode")
        num_records = len(addresses).to_bytes(1, "big")
        data = num_records + b"".join(BIP155Like.encode(addr) for addr in addresses)
        log.debug("Full payload: %s", data)

        s = io.BytesIO(data)
        records = []
        for pos in range(AAAACodec.RECORD_LIMIT):
            payload = s.read(AAAACodec.PAYLOAD_BYTES)
            if not payload:
                break
            if len(payload) < AAAACodec.PAYLOAD_BYTES:
                payload += b"\x00" * (AAAACodec.PAYLOAD_BYTES - len(payload))
            assert AAAACodec.PREFIX.prefixlen % 8 == 0, "Prefix must be byte-aligned"
            pfxlen = int(AAAACodec.PREFIX.prefixlen / 8)
            pfx = AAAACodec.PREFIX.network_address.packed[:pfxlen]
            ip = str(ipaddress.IPv6Address(pfx + pos.to_bytes(1, "big") + payload))
            print(AAAACodec.PREFIX)
            log.debug("Encoding payload %s into address %s", payload, ip)
            rdata = AAAA(IN, AAAA_TYPE, ip)
            record = dns.rrset.from_rdata(domain, ttl, rdata)
            records.append(record)

        if s.tell() != len(data):
            raise ValueError("Could not encode all data!")
        log.debug(
            "Encoded %d addresses into %d AAAA records",
            len(addresses),
            len(records),
        )
        random.shuffle(records)
        return records
