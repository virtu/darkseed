"""Module for DNS-related functionality."""

from .custom_encoder import CustomNullEncoding
from .record_builder import RecordBuilder
from .server import DNSConstants, DNSServer

__all__ = [
    "CustomNullEncoding",
    "DNSConstants",
    "DNSServer",
    "RecordBuilder",
]
