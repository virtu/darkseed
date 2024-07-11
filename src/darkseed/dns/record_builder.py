"""Module for DNS records encoding and decoding functionality."""

import logging as log

import dns.rrset
from dns.rdata import Rdata
from dns.rdataclass import IN
from dns.rdatatype import AAAA as AAAA_TYPE
from dns.rdatatype import TXT as TXT_TYPE
from dns.rdatatype import A as A_TYPE
from dns.rdtypes.ANY.TXT import TXT
from dns.rdtypes.IN.A import A
from dns.rdtypes.IN.AAAA import AAAA

from darkseed.node import Address, AddressCodec

# todos:
# - avoid dups
# - inbue with domain knowledge (e.g., if CJDNS, I2P, and TOR records exist,
#   provide at least one of the two former, two of the latter)


class RecordBuilder:
    """Class for building DNS resource records."""

    @staticmethod
    def build_record(
        address: Address,
        encoding: str = "address",
        domain: str = "seed.21.ninja.",
        ttl: int = 60,
    ) -> dns.rrset:
        """Build a DNS record for a node using the specified encoding."""

        rdata = RecordBuilder.get_rdata(address, encoding)

        record = dns.rrset.from_rdata(domain, ttl, rdata)

        log.debug(
            "RR for address=%s: rdata=%s, rr=%s",
            address,
            rdata,
            record,
        )
        return record

    @staticmethod
    def get_rdata(address: Address, encoding: str = "address") -> Rdata:
        """
        Get DNS resource record data.

        Always use 'address' encoding for IPv4, IPv6, and CJDNS addresses.
        """
        if encoding != "address" and (address.ipv4 or address.ipv6 or address.cjdns):
            log.warning(
                "Encoding '%s' not supported for %s. Defaulting to 'address' encoding!",
                encoding,
                address.net_type,
            )

        if address.ipv4:
            return A(IN, A_TYPE, address.address)
        if address.ipv6 or address.cjdns:
            return AAAA(IN, AAAA_TYPE, address.address)
        if encoding == "address" and address.onion or address.i2p:
            return TXT(IN, TXT_TYPE, [address.address])

        data = AddressCodec.encode_address(address, encoding)
        return TXT(IN, TXT_TYPE, [data])
