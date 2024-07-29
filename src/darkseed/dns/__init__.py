"""Module for DNS-related functionality."""

from .custom_encoder import CustomNullEncoding
from .record_builder import RecordBuilder
from .server import DNSResponder, DNSServer

__all__ = [
    "RecordBuilder",
    "DNSResponder",
    "DNSServer",
    "CustomNullEncoding",
]
