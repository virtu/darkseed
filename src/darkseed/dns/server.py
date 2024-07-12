"""DNS functionality for Darkseed."""

import logging as log
import random
import socketserver
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import ClassVar, List

import dns.message
import dns.rdatatype
import dns.rrset

from darkseed.node import Node

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

        # TODO: abstract and move into function!
        # encode two onion and i2p addrs using MultiAddressCodec
        onion_nodes = [node for node in self.reachable_nodes if node.address.onion]
        onion_nodes = random.sample(onion_nodes, 2)
        i2p_nodes = [node for node in self.reachable_nodes if node.address.i2p]
        i2p_nodes = random.sample(i2p_nodes, 2)
        addrs = [n.address for n in onion_nodes + i2p_nodes]
        record = MultiAddressCodec.build_record(addrs)
        num_recs += 4
        response.answer.append(record)
        log.debug(
            "Added four records to response (num_recs=%d, size=%dB)",
            num_recs,
            len(response.to_wire()),
        )

        # TODO: abstract and move into function
        cjdns_addrs = [n.address for n in self.reachable_nodes if n.address.cjdns]
        cjdns_addrs = random.sample(cjdns_addrs, 2)
        for cjdns_addr in cjdns_addrs:
            record = RecordBuilder.build_record(cjdns_addr)
            response.answer.append(record)
        num_recs += 2
        log.debug(
            "Added 2 records to response (num_recs=%d, size=%dB)",
            num_recs,
            len(response.to_wire()),
        )

        # TODO: abstract and move into function
        ipv4_addrs = [n.address for n in self.reachable_nodes if n.address.ipv4]
        ipv4_addrs = random.sample(ipv4_addrs, 10)
        for ipv4_addr in ipv4_addrs:
            record = RecordBuilder.build_record(ipv4_addr)
            response.answer.append(record)
        num_recs += 10
        log.debug(
            "Added 10 records to response (num_recs=%d, size=%dB)",
            num_recs,
            len(response.to_wire()),
        )

        # TODO: abstract and move into function
        ipv6_addrs = [n.address for n in self.reachable_nodes if n.address.ipv6]
        ipv6_addrs = random.sample(ipv6_addrs, 4)
        for ipv6_addr in ipv6_addrs:
            record = RecordBuilder.build_record(ipv6_addr)
            response.answer.append(record)
        num_recs += 4
        log.debug(
            "Added 4 records to response (num_recs=%d, size=%dB)",
            num_recs,
            len(response.to_wire()),
        )

        log.info(
            "Created response (size=%dB, records=%d, hex=%s)",
            len(response.to_wire()),
            num_recs,
            response.to_wire().hex(),
        )
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
