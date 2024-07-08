"""
DNS functionality for Darkseed

Components:
- DNSServer
- DNSRequestHandler
"""

import copy
import logging as log
import random
import socketserver
import threading
import time
from dataclasses import dataclass, field

from dnslib import AAAA, QTYPE, RR, TXT, A, DNSRecord

# Generate dummy records until real data is read from crawler outputs
SeedRecords = []
for i in range(20):
    SeedRecords.append((QTYPE.A, A(f"192.168.178.{i}")))
    SeedRecords.append((QTYPE.AAAA, AAAA(f"ff06:f00d::10:{i}")))
    SeedRecords.append((QTYPE.TXT, TXT(f"Test data {i}")))


@dataclass
class NodeAddress:
    """Class representing a Bitcoin node address."""

    address: str
    port: int
    network: str

    def get_rtype_rdata(self):
        """Convert address to DNS resource record (type, data)-pair."""
        if self.network == "ipv4":
            return QTYPE.A, A(self.address)
        if self.network == "ipv6":
            return QTYPE.AAAA, AAAA(self.address)
        if self.network == "onion_v3":
            return QTYPE.TXT, TXT(self.address)
        if self.network == "onion_v3":
            return QTYPE.TXT, TXT(self.address)
        if self.network == "onion_v3":
            return QTYPE.TXT, TXT(self.address)
        raise ValueError(f"Unknown network: {self.network}")


class DNSRequestHandler:
    """DNS request handler."""

    reachable_nodes: list = field(default_factory=list)

    def set_reachable_nodes(self, nodes):
        """Set reachable nodes."""
        log.debug(
            "DNSRequestHandler.set_reachable_nodes() called with %d nodes", len(nodes)
        )
        self.reachable_nodes = nodes

    def handle(self, request, address):
        """Handle DNS request: marshall data and send reply."""
        log.debug("Received DNS request from %s", address)
        data = request[0].strip()
        reply = self.get_reply(data)
        socket = request[1]
        socket.sendto(reply, address)
        log.debug("Sent DNS reply (size=%d, to=%s)", len(reply), address)

    def get_reply(self, data) -> bytearray:
        """Get DNS reply."""

        request = DNSRecord.parse(data)
        reply = request.reply()
        if not self.reachable_nodes:
            log.warning("No reachable nodes to reply with: returning empty reply.")
            return bytearray()
        pool = self.reachable_nodes.copy()
        # pool = SeedRecords.copy()

        num_recs = 0
        size_limit = 512

        while True:
            if not pool:
                log.warning("Ran out of reachable nodes during reply creation.")
                if num_recs == 0:
                    log.warning("Returning empty reply")
                return reply.pack()

            # rtype, rdata = random.choice(pool)
            address = random.choice(pool)
            rtype, rdata = address.get_rtype_rdata()
            log.debug("attempting to add rtype=%s, rdata=%s", rtype, rdata)
            # todos:
            # - avoid dups
            # - inbue with domain knowledge (e.g., if CJDNS, I2P, and TOR records exist,
            #   provide at least one of the two former, two of the latter)
            rrec = RR("seed.21.ninja", rtype=rtype, ttl=60, rdata=rdata)

            reply_new = copy.deepcopy(reply)
            reply_new.add_answer(rrec)

            if len(reply_new.pack()) > size_limit:
                # exit early. room for opt: try another record
                log.debug(
                    "new_size=%dB exceeds limit=%dB", len(reply_new.pack()), size_limit
                )
                break

            num_recs += 1
            log.debug(
                "Added record (data=%s, type=%s, number=%d, prev_size=%dB, new_size=%dB)",
                rrec.rdata,
                rrec.rtype,
                num_recs,
                len(reply.pack()),
                len(reply_new.pack()),
            )
            reply = reply_new

        log.info("Created reply (size=%dB, records=%d)", len(reply.pack()), num_recs)
        # log.info("Reply: %s", reply)
        # log.info("dir(reply): %s", dir(reply))
        # log.info("reply.questions: %s", reply.questions)
        # log.info("reply.reply: %s", reply.reply)
        return reply.pack()


dns_request_handler = DNSRequestHandler()


class DNSRequestBridge(socketserver.BaseRequestHandler):
    """DNS request handler called by DNSServer when a request is received."""

    def handle(self):
        """Bridge DNS request to DNSRequestHandler."""
        dns_request_handler.handle(self.request, self.client_address)  # ignore: type


@dataclass(unsafe_hash=True)
class DNSServer(threading.Thread):
    """DNS server."""

    address: str
    port: int
    # node_provider: NodeProvider

    def __post_init__(self):
        super().__init__(name=self.__class__.__name__)

    def start(self):
        """Start DNS server thread."""
        log.info("Starting DNS server on %s:%d", self.address, self.port)
        server = socketserver.UDPServer((self.address, self.port), DNSRequestBridge)
        # server.node_provider = self.node_provider  # type: ignore
        server.serve_forever()
