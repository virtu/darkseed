"""Module for DNS-related functionality."""

from .aaaa_record import AAAARecord, AAAARecordCodec
from .null_record import NullRecord, NullRecordCodec
from .regular_records import RegularRecords
from .server import DNSConstants, DNSServer

__all__ = [
    "DNSConstants",
    "DNSServer",
    "RegularRecords",
    "NullRecord",
    "NullRecordCodec",
    "AAAARecord",
    "AAAARecordCodec",
]
