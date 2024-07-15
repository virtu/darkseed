"""Module for DNS records encoding and decoding functionality."""

import logging as log

import dns.rdata
import dns.rrset
from dns.rdataclass import IN
from dns.rdatatype import AAAA as AAAA_TYPE
from dns.rdatatype import A as A_TYPE
from dns.rdtypes.IN.A import A
from dns.rdtypes.IN.AAAA import AAAA

from darkseed.node import Address


class RecordBuilder:
    """Class for building DNS resource records."""

    @staticmethod
    def build_record(
        address: Address, domain: str = "seed.21.ninja.", ttl: int = 60
    ) -> dns.rrset.RRset:
        """Build a DNS record for a node using the specified encoding."""
        if not (address.ipv4 or address.ipv6 or address.cjdns):
            raise ValueError(f"Unsupported address type: {address.net_type}")

        rdata = RecordBuilder.get_rdata(address)
        record = dns.rrset.from_rdata(domain, ttl, rdata)

        log.debug(
            "RR for address=%s: rdata=%s, rr=%s",
            address,
            rdata.to_wire().hex(),
            record,
        )
        return record

    @staticmethod
    def get_rdata(address: Address) -> dns.rdata.Rdata:
        """Get DNS resource record data."""
        if address.ipv4:
            return A(IN, A_TYPE, address.address)
        if address.ipv6 or address.cjdns:
            return AAAA(IN, AAAA_TYPE, address.address)
        raise ValueError(f"Unsupported address type: {address.net_type}")
