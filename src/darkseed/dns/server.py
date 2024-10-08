"""DNS functionality for Darkseed."""

import ipaddress
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

from darkseed.address import Address, NetworkType
from darkseed.node_manager import NodeManager

from .aaaa_codec import AAAACodec
from .regular_records import RegularRecords


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

    @staticmethod
    def question_to_netcounts(question: dns.rrset.RRset) -> dict[NetworkType, int]:
        """Map question (in particular, domain and type) to network counts."""
        qtype = question.rdtype
        qdomain = question.name.to_text(omit_final_dot=False).lower()
        zone = DNSHandler._ZONE
        assert qdomain.endswith(zone), f"Error: {qdomain} does not end with {zone}"
        subdomain = qdomain[: -len(zone) - 1]  # remove trailing dot
        match (subdomain, qtype):
            # first match takes care of ANY and no subdomain in the two following matches
            case ("", dns.rdatatype.ANY):
                result = {NetworkType.IPV4: 12, NetworkType.IPV6: 10}
            case ("" | "n1", dns.rdatatype.A | dns.rdatatype.ANY):
                result = {NetworkType.IPV4: 29}
            case ("" | "n2", dns.rdatatype.AAAA | dns.rdatatype.ANY):
                result = {NetworkType.IPV6: 16}
            case ("n3", dns.rdatatype.AAAA | dns.rdatatype.ANY):
                result = {NetworkType.ONION_V3: 6}
            case ("n4", dns.rdatatype.AAAA | dns.rdatatype.ANY):
                result = {NetworkType.I2P: 6}
            case ("n5", dns.rdatatype.AAAA | dns.rdatatype.ANY):
                result = {NetworkType.CJDNS: 13}
            case _:
                result = {}
        return result

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
            log.warning(
                "Refusing DNS query with more than one question: from=%s, size=%d, questions=%d",
                peer_info,
                len(data),
                len(request.question),
            )
            return cls.refuse(request)

        question = request.question[0]
        qdomain = question.name.to_text(omit_final_dot=False).lower()
        if not qdomain.endswith(cls._ZONE):
            log.warning(
                "Silently dropping DNS query for unknown zone: from=%s, size=%d, name=%s",
                peer_info,
                len(data),
                qdomain,
            )
            return bytes()

        if question.rdtype not in (
            dns.rdatatype.A,
            dns.rdatatype.AAAA,
            dns.rdatatype.ANY,
        ):
            log.warning(
                "Refusing DNS query for unsupported query type: from=%s, size=%d, name=%s, type=%s",
                peer_info,
                len(data),
                qdomain,
                dns.rdatatype.to_text(question.rdtype),
            )
            return cls.refuse(request)

        log.info(
            "Received DNS query: from=%s, size=%d, domain=%s, class=%s, type=%s",
            peer_info,
            len(data),
            qdomain,
            dns.rdataclass.to_text(question.rdclass),
            dns.rdatatype.to_text(question.rdtype),
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
    def select_addresses(question: dns.rrset.RRset) -> List[Address]:
        """Get addresses based on RDTYPE in request.

        First, look up address types and corresponding numbers to select using
        RDTYPE. Then, request the data from the NodeManager.
        """

        net_to_addr_num = DNSHandler.question_to_netcounts(question)
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
        addresses = DNSHandler.select_addresses(question)
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

        clearnet_addrs = [a for a in addresses if a.ipv4 or a.ipv6]
        for address in clearnet_addrs:
            record = RegularRecords.build_record(address, domain)
            response.answer.append(record)

        darknet_addrs = [a for a in addresses if not (a.ipv4 or a.ipv6)]
        if darknet_addrs:
            records = AAAACodec.encode(darknet_addrs, domain)
            for record in records:
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

    address: str
    port: int
    zone: str
    node_manager: NodeManager

    def __post_init__(self):
        super().__init__(name=self.__class__.__name__)
        DNSHandler.set_node_manager(self.node_manager)
        DNSHandler.set_zone(self.zone)

    @staticmethod
    def get_peer_info(client_address: Tuple[str, int], protocol: str) -> str:
        """Convert client address into peer string."""
        address, port = client_address
        ban = ipaddress.ip_network(f"{address}/16", strict=False)
        return f"{address}:{port} (ban={ban}) [{protocol}]"

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
            _start_server(self.address, self.port, proto)


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
        peer_info = DNSServer.get_peer_info(self.client_address, protocol="TCP")
        response = DNSHandler.process(data[2:], peer_info)
        # no response means the request should be ignored silently
        if not response:
            return
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
        peer_info = DNSServer.get_peer_info(self.client_address, protocol="UDP")
        response = DNSHandler.process(data, peer_info)
        # no response means the request should be ignored silently
        if not response:
            return
        socket = self.request[1]
        size, limit = len(response), DNSConstants.UDP_SIZE_LIMIT
        assert size <= limit, f"Response too large (size={size}, limit={limit})"
        socket.sendto(response, self.client_address)
