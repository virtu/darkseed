"""Module for DNS-related functionality."""

from .custom_encoder import CustomNullEncoding
from .record_builder import RecordBuilder
from .server import DNSResponder, DNSServer, dns_responder

__all__ = [
    "RecordBuilder",
    "DNSResponder",
    "DNSServer",
    "dns_responder",
    "CustomNullEncoding",
]
