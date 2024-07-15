"""DNS functionality for Darkseed."""

import logging as log
import random
import socketserver
import threading
from dataclasses import dataclass, field
from typing import ClassVar, List

import dns.message
import dns.rdatatype
import dns.rrset

from darkseed.node import Address, Node

from .custom_encoder import MultiAddressCodec
from .record_builder import RecordBuilder


class DNSResponder:
    """DNS responder."""

    reachable_nodes: List[Node] = field(default_factory=list)
    REPLY_SIZE_LIMIT: ClassVar[int] = 512

    def set_reachable_nodes(self, nodes):
        """Set reachable nodes."""
        self.reachable_nodes = nodes
        log.info(
            "Updated reachable node pool: total=%d, ipv4=%d, ipv6=%d, onion_v3=%d, i2p=%d, cjdns=%d",
            len(nodes),
            len([n for n in nodes if n.address.ipv4]),
            len([n for n in nodes if n.address.ipv6]),
            len([n for n in nodes if n.address.onion]),
            len([n for n in nodes if n.address.i2p]),
            len([n for n in nodes if n.address.cjdns]),
        )

    def handle(self, request, address):
        """Handle DNS request: marshall data and send response."""
        data, socket = request[0].strip(), request[1]
        request = dns.message.from_wire(data)
        domain = [q.name.to_text(omit_final_dot=True) for q in request.question]
        log.debug("Received DNS request from %s for %s", address, domain)
        response = self.create_response(request)
        socket.sendto(response, address)
        log.debug("Sent DNS response (size=%d, to=%s)", len(response), address)

    def get_random_addresses(self, address_type: str, count: int):
        """Select a specific number of address based on address type."""
        nodes = [n for n in self.reachable_nodes if getattr(n.address, address_type)]
        addresses = [n.address for n in nodes]
        if len(nodes) < count:
            log.warning(
                "Not enough nodes to select from: count=%d, total=%d. Returning %d address(es).",
                count,
                len(nodes),
                len(nodes),
            )
        return random.sample(addresses, min(count, len(nodes)))

    def add_records_to_response(
        self, response, addresses: List[Address], encoding: str = "regular"
    ):
        """Add records for the nodes to the DNS response."""
        if encoding == "regular":
            for address in addresses:
                record = RecordBuilder.build_record(address)
                response.answer.append(record)
            num_recs, num_addrs = len(addresses), len(addresses)
        elif encoding == "custom":
            record = MultiAddressCodec.build_record(addresses)
            response.answer.append(record)
            num_recs, num_addrs = 1, len(addresses)
        else:
            raise ValueError(f"Invalid encoding: {encoding}")
        size = len(response.to_wire())
        log.debug(
            "Added %d record(s) for %d address(es) to response (size=%dB)",
            num_recs,
            num_addrs,
            size,
        )

    def create_response(self, request) -> bytes:
        """Create DNS response."""
        # TODO: output error if we run out of nodes or there's an issue with
        # the reply's size

        response = dns.message.make_response(request)
        response.use_edns(False)

        if not self.reachable_nodes:
            log.warning("No reachable nodes to response with: empty response.")
            return bytes()
        num_recs = 0

        num_darknet, num_ipv4, num_ipv6 = 2, 10, 4

        # add onion and cjdns nodes using custom encoding
        onion_nodes = self.get_random_addresses("onion", num_darknet)
        i2p_nodes = self.get_random_addresses("i2p", num_darknet)
        multi_addrs = onion_nodes + i2p_nodes
        self.add_records_to_response(response, multi_addrs, "custom")

        # add nodes with A and AAAA records
        self.add_records_to_response(
            response, self.get_random_addresses("cjdns", num_darknet)
        )
        self.add_records_to_response(
            response, self.get_random_addresses("ipv4", num_ipv4)
        )
        self.add_records_to_response(
            response, self.get_random_addresses("ipv6", num_ipv6)
        )

        log.info(
            "Created response (size=%dB, records=%d)", len(response.to_wire()), num_recs
        )
        log.debug("Response=%s", response.to_wire().hex())
        return response.to_wire()


dns_responder = DNSResponder()


class DNSRequestBridge(socketserver.BaseRequestHandler):
    """
    Class to bridge between UDPServer and DNSResponder.

    This is necessary because the BaseRequestHandler class, which this class
    inherits from, cannot easily be extended.
    """

    def handle(self):
        """Bridge DNS request to DNSResponder."""
        dns_responder.handle(self.request, self.client_address)


@dataclass(unsafe_hash=True)
class DNSServer(threading.Thread):
    """DNS server."""

    address: str
    port: int

    def __post_init__(self):
        super().__init__(name=self.__class__.__name__)

    def start(self):
        """Start DNS server thread."""
        log.info("Starting DNS server on %s:%d", self.address, self.port)
        server = socketserver.UDPServer((self.address, self.port), DNSRequestBridge)
        server.serve_forever()
