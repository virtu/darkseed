"""Module for DNS-related functionality."""

from .aaaa_codec import AAAACodec
from .regular_records import RegularRecords
from .server import DNSConstants, DNSServer

__all__ = [
    "AAAACodec",
    "DNSConstants",
    "DNSServer",
    "RegularRecords",
]
