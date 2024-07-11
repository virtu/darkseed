"""Module for DNS-related functionality."""

from .record_builder import RecordBuilder
from .server import DNSResponder, DNSServer, dns_responder

__all__ = ["RecordBuilder", "DNSResponder", "DNSServer", "dns_responder"]
