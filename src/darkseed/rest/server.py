"""REST API server for Darkseed."""

import logging as log
import random
from threading import Thread

from flask import Flask, jsonify


class RESTServer:
    """REST API server for Darkseed."""

    def __init__(self, address: str, port: int):
        self.app = Flask(__name__)
        self.reachable_nodes = []
        self.address = address
        self.port = port
        self.server_thread = None
        self.setup_routes()

    def setup_routes(self):
        """Setup routes for the REST API."""

        @self.app.route("/nodes", methods=["GET"])
        def get_nodes():
            """Get reachable nodes of different network types."""
            return self._get_nodes_response()

        @self.app.route("/nodes/ipv4", methods=["GET"])
        def get_ipv4_nodes():
            """Get reachable IPv4 nodes."""
            return self._get_nodes_response(node_type="ipv4")

        @self.app.route("/nodes/ipv6", methods=["GET"])
        def get_ipv6_nodes():
            """Get reachable IPv6 nodes."""
            return self._get_nodes_response(node_type="ipv6")

        @self.app.route("/nodes/onion", methods=["GET"])
        def get_onion_nodes():
            """Get reachable Onion nodes."""
            return self._get_nodes_response(node_type="onion")

        @self.app.route("/nodes/i2p", methods=["GET"])
        def get_i2p_nodes():
            """Get reachable I2P nodes."""
            return self._get_nodes_response(node_type="i2p")

        @self.app.route("/nodes/cjdns", methods=["GET"])
        def get_cjdns_nodes():
            """Get reachable CJDNS nodes."""
            return self._get_nodes_response(node_type="cjdns")

    def _get_nodes_response(self, node_type=None, num_requested=32):
        """Select a specific number of address based on address type."""
        if not self.reachable_nodes:
            return jsonify({"error": "No reachable nodes available"}), 500

        addresses = [n.address for n in self.reachable_nodes]
        if node_type:
            addresses = [a for a in addresses if getattr(a, node_type)]
        num_available = len(addresses)
        num_addresses = min(num_requested, num_available)
        if num_addresses < num_requested:
            log.warning(
                "Insufficient addresses (requested=%d, available=%d): returning %d.",
                num_requested,
                num_available,
                num_addresses,
            )
        addresses = random.sample(addresses, num_addresses)
        return jsonify(addresses), 200

    def start(self):
        """Start REST server thread."""
        self.server_thread = Thread(
            target=self.app.run, kwargs={"host": self.address, "port": self.port}
        )
        self.server_thread.start()
        log.info("Started RESTServer on %s:%d.", self.address, self.port)

    def set_reachable_nodes(self, nodes):
        """Set reachable nodes."""
        self.reachable_nodes = nodes
        log.info(
            "Updated reachable node pool for RESTServer: total=%d, ipv4=%d, ipv6=%d, onion_v3=%d, i2p=%d, cjdns=%d",
            len(nodes),
            len([n for n in nodes if n.address.ipv4]),
            len([n for n in nodes if n.address.ipv6]),
            len([n for n in nodes if n.address.onion]),
            len([n for n in nodes if n.address.i2p]),
            len([n for n in nodes if n.address.cjdns]),
        )

    def get_update_function(self):
        """Return the set_reachable_nodes function of the DNSResponder."""
        return self.set_reachable_nodes
