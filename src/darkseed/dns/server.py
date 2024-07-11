"""DNS functionality for Darkseed."""

import copy
import logging as log
import random
import socketserver
import threading
from dataclasses import dataclass, field
from typing import List

import dns.message
import dns.rdatatype
import dns.rrset

from darkseed.node import Node

from .record_builder import RecordBuilder


class DNSResponder:
    """DNS responder."""

    reachable_nodes: List[Node] = field(default_factory=list)

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
        """Handle DNS request: marshall data and send reply."""
        data, socket = request[0].strip(), request[1]
        request = dns.message.from_wire(data)
        domain = [q.name.to_text(omit_final_dot=True) for q in request.question]
        log.debug("Received DNS request from %s for %s", address, domain)
        reply = self.create_response(request)
        socket.sendto(reply, address)
        log.debug("Sent DNS reply (size=%d, to=%s)", len(reply), address)

    def create_response(self, request) -> bytearray:
        """Create DNS response."""

        reply = dns.message.make_response(request)

        if not self.reachable_nodes:
            log.warning("No reachable nodes to reply with: returning empty reply.")
            return bytearray()

        # TODO
        # - avoid dups
        # - inbue with domain knowledge (e.g., if CJDNS, I2P, and TOR records exist,
        #   provide at least one of the two former, two of the latter)
        # - log if we run out of nodes or reply no nodes
        # - size_limit: create CONST and store somewhere
        size_limit = 512
        num_recs = 0

        nodes_pool = self.reachable_nodes.copy()
        while nodes_pool and len(reply.to_wire()) < size_limit:
            node = random.choice(nodes_pool)
            record = RecordBuilder.build_record(node.address)
            reply.answer.append(record)
            if len(reply.to_wire()) > size_limit:
                log.debug(
                    "new_size=%dB for %d records exceeds limit=%dB",
                    len(reply.to_wire()),
                    num_recs + 1,
                    size_limit,
                )
                reply.answer.pop()
                break
            num_recs += 1
            log.debug(
                "Added record for address=%s (num_recs=%d, size=%dB): %s",
                node.address,
                num_recs,
                len(reply.to_wire()),
                record,
            )

        log.info("Created reply (size=%dB, records=%d)", len(reply.to_wire()), num_recs)
        return reply.to_wire()


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
