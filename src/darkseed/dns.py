"""DNS functionality for Darkseed."""

import copy
import logging as log
import random
import socketserver
import threading
from dataclasses import dataclass, field
from typing import List

from dnslib import RR, DNSRecord

from darkseed.codec import Codec
from darkseed.node import Node


class DNSRequestHandler:
    """DNS request handler."""

    reachable_nodes: List[Node] = field(default_factory=list)

    def set_reachable_nodes(self, nodes):
        """Set reachable nodes."""
        self.reachable_nodes = nodes
        log.info(
            "Updated reachable node pool: total=%d, ipv4=%d, ipv6=%d, onion_v3=%d, i2p=%d, cjdns=%d",
            len(nodes),
            len([n for n in nodes if n.network == "ipv4"]),
            len([n for n in nodes if n.network == "ipv6"]),
            len([n for n in nodes if n.network == "onion_v3"]),
            len([n for n in nodes if n.network == "i2p"]),
            len([n for n in nodes if n.network == "cjdns"]),
        )

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

        nodes_pool = self.reachable_nodes.copy()
        num_recs = 0
        size_limit = 512
        while True:
            if not nodes_pool:
                log.warning("Ran out of reachable nodes during reply creation.")
                if num_recs == 0:
                    log.warning("Returning empty reply")
                return reply.pack()

            # rtype, rdata = random.choice(pool)
            node = random.choice(nodes_pool)
            rtype = Codec.get_rtype(node.address)
            rdata = Codec.get_rdata(node.address)
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
        return reply.pack()


dns_request_handler = DNSRequestHandler()


class DNSRequestBridge(socketserver.BaseRequestHandler):
    """
    Class to bridge between UDPServer and DNSRequestHandler.

    This is necessary because the BaseRequestHandler class, which this class
    inherits from, cannot easily be extended.
    """

    def handle(self):
        """Bridge DNS request to DNSRequestHandler."""
        dns_request_handler.handle(self.request, self.client_address)


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
