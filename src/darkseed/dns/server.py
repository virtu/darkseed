"""DNS functionality for Darkseed."""

import logging as log
import socketserver
import threading
from dataclasses import dataclass
from typing import ClassVar, List, Tuple

import dns.message
import dns.rcode
import dns.rdataclass
import dns.rdatatype
import dns.rrset

from darkseed.config import DNSConfig
from darkseed.node import Address, NetworkType
from darkseed.node_manager import NodeManager

from .custom_encoder import MultiAddressCodec
from .record_builder import RecordBuilder


@dataclass
class DNSConstants:
    """DNS protocol constants."""

    UDP_SIZE_LIMIT: ClassVar[int] = 512
    TCP_SIZE_LIMIT: ClassVar[int] = 65535


@dataclass
class DNSHandler:
    """Class for handling DNS requests.

    Uses a NodeManager to marshall nodes for response.
    """

    _NODE_MANAGER: ClassVar[NodeManager]
    _ZONE: ClassVar[str]
    RDTYPE_TO_NETCOUNT: ClassVar[
        dict[dns.rdatatype.RdataType, dict[NetworkType, int]]
    ] = {
        dns.rdatatype.A: {NetworkType.IPV4: 29},
        dns.rdatatype.AAAA: {NetworkType.IPV6: 17},
        dns.rdatatype.NULL: {
            NetworkType.ONION_V3: 5,
            NetworkType.I2P: 5,
            NetworkType.CJDNS: 4,
        },
        dns.rdatatype.ANY: {
            NetworkType.IPV4: 10,
            NetworkType.IPV6: 4,
            NetworkType.ONION_V3: 2,
            NetworkType.I2P: 2,
            NetworkType.CJDNS: 2,
        },
    }

    @classmethod
    def set_node_manager(cls, node_manager):
        """Set the node manager."""
        cls._NODE_MANAGER = node_manager

    @classmethod
    def set_zone(cls, zone: str):
        """Set the zone manager."""
        cls._ZONE = zone

    @classmethod
    def refuse(cls, request: dns.message.Message) -> bytes:
        """Create serialized DNS reply indicating the request was refused."""
        response = dns.message.make_response(request)
        response.set_rcode(dns.rcode.REFUSED)
        return response.to_wire()

    @classmethod
    def process(cls, data: bytes, peer_info: str) -> bytes:
        """Process DNS request."""
        if not getattr(cls, "_NODE_MANAGER", None):
            raise RuntimeError(f"{cls.__name__}: Node manager not set")
        if not getattr(cls, "_ZONE", None):
            raise RuntimeError(f"{cls.__name__}: Zone not set")

        request = dns.message.from_wire(data)
        if len(request.question) != 1:
            log.warning("Refusing request with more than one question")
            return cls.refuse(request)

        question = request.question[0]
        qdomain = question.name.to_text(omit_final_dot=False).lower()
        if qdomain != cls._ZONE:
            log.warning("Refusing request for unknown zone (name=%s)", qdomain)
            return cls.refuse(request)

        log.info(
            "Received DNS query: from=%s, size=%s, domain=%s, class=%s, type=%s",
            peer_info,
            len(data),
            qdomain,
            dns.rdatatype.to_text(question.rdtype),
            dns.rdataclass.to_text(question.rdclass),
        )
        response_bytes, response_records = cls.create_response(request)
        log.info(
            "Sending reply: to=%s, size=%d, records=%d",
            peer_info,
            len(response_bytes),
            response_records,
        )
        return response_bytes

    @staticmethod
    def select_addresses(rdtype: dns.rdatatype.RdataType) -> List[Address]:
        """Get addresses based on RDTYPE in request.

        First, look up address types and corresponding numbers to select using
        RDTYPE. Then, request the data from the NodeManager.
        """
        net_to_addr_num = DNSHandler.RDTYPE_TO_NETCOUNT[rdtype]
        addresses = []
        for net, count in net_to_addr_num.items():
            if count:
                addresses += DNSHandler._NODE_MANAGER.get_random_addresses(net, count)
        return addresses

    @staticmethod
    def create_response(request: dns.message.Message) -> Tuple[bytes, int]:
        """Create DNS response."""
        response = dns.message.make_response(request)
        response.use_edns(False)
        question = request.question[0]
        addresses = DNSHandler.select_addresses(question.rdtype)
        DNSHandler.add_records_to_response(response, addresses)
        log.debug(
            "Created response (size=%dB, records=%d)",
            len(response.to_wire()),
            len(addresses),
        )
        log.debug("Response=%s", response.to_wire().hex())
        return response.to_wire(), len(addresses)

    @staticmethod
    def add_records_to_response(
        response: dns.message.Message, addresses: List[Address]
    ):
        """Add address records to the DNS response.

        1. Add individual regular record for each clearnet addresses
        2. Add consolidated compressed record for all darknet addresses
        """

        domain = response.question[0].name.to_text(omit_final_dot=False)

        clearnet_addrs = [a for a in addresses if a.ipv4 or a.ipv6 or a.cjdns]
        for address in clearnet_addrs:
            record = RecordBuilder.build_record(address, domain)
            response.answer.append(record)

        darknet_addrs = [a for a in addresses if not (a.ipv4 or a.ipv6 or a.cjdns)]
        if darknet_addrs:
            record = MultiAddressCodec.build_record(darknet_addrs, domain)
            response.answer.append(record)

        size = len(response.to_wire())
        log.debug(
            "Added %d record(s) for %d address(es) to response (size=%dB)",
            len(clearnet_addrs) + 1,
            len(clearnet_addrs) + len(darknet_addrs),
            size,
        )


@dataclass(unsafe_hash=True)
class DNSServer(threading.Thread):
    """DNS server."""

    config: DNSConfig
    node_manager: NodeManager

    def __post_init__(self):
        super().__init__(name=self.__class__.__name__)
        DNSHandler.set_node_manager(self.node_manager)
        DNSHandler.set_zone(self.config.zone)

    def run(self):
        """Start TCP and UDP DNS server threads."""

        def _start_server(address, port, protocol):
            """Start DNS server."""
            if protocol == "TCP":
                server = socketserver.TCPServer((address, port), TCPRequestHandler)
            elif protocol == "UDP":
                server = socketserver.UDPServer((address, port), UDPRequestHandler)
            else:
                raise ValueError(f"Unsupported protocol {protocol}")
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.start()
            log.info("Started DNS server on %s:%d [%s]", address, port, protocol)

        for proto in ("TCP", "UDP"):
            _start_server(self.config.address, self.config.port, proto)


class TCPRequestHandler(socketserver.BaseRequestHandler):
    """TCP request handler for DNS requests."""

    def handle(self):
        """Handle DNS request."""
        log.debug("Received TCP packet (request=%s)", self.request)
        data = self.request.recv(DNSConstants.TCP_SIZE_LIMIT)
        expected_size = int.from_bytes(data[:2], byteorder="big")
        if len(data) - 2 != expected_size:
            log.warning(
                "Received invalid TCP DNS packet (expected=%d, actual=%d)",
                expected_size,
                len(data),
            )
            return
        peer_info = ":".join(str(x) for x in self.client_address) + " [TCP]"
        response = DNSHandler.process(data[2:], peer_info)
        size, limit = len(response), DNSConstants.TCP_SIZE_LIMIT
        assert size <= limit, f"Response too large (size={size}, limit={limit})"
        log.debug("Sending TCP packet (to=%s, data=%s)", self.client_address, response)
        size = len(response).to_bytes(2, byteorder="big")
        self.request.sendall(size + response)


class UDPRequestHandler(socketserver.BaseRequestHandler):
    """UDP request handler for DNS requests."""

    def handle(self):
        """Handle DNS request."""
        data = self.request[0].strip()
        peer_info = ":".join(str(x) for x in self.client_address) + " [UDP]"
        response = DNSHandler.process(data, peer_info)
        socket = self.request[1]
        size, limit = len(response), DNSConstants.UDP_SIZE_LIMIT
        assert size <= limit, f"Response too large (size={size}, limit={limit})"
        socket.sendto(response, self.client_address)
