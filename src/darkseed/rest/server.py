"""REST API server for Darkseed."""

import logging as log
from threading import Thread

from flask import Flask, jsonify

from darkseed.node import NetworkType
from darkseed.node_manager import NodeManager


class RESTServer:
    """REST API server for Darkseed."""

    def __init__(self, address: str, port: int, node_manager: NodeManager):
        self.app = Flask(__name__)
        self.reachable_nodes = []
        self.address = address
        self.port = port
        self.node_manager = node_manager
        self.server_thread = None
        self.setup_routes()

    def setup_routes(self):
        """Setup routes for the REST API."""

        @self.app.route("/nodes", methods=["GET"])
        def get_nodes():
            """Get reachable nodes of different network types."""
            addresses = self.node_manager.get_random_addresses(NetworkType.IPV4, 7)
            addresses += self.node_manager.get_random_addresses(NetworkType.IPV6, 7)
            addresses += self.node_manager.get_random_addresses(NetworkType.ONION_V3, 6)
            addresses += self.node_manager.get_random_addresses(NetworkType.I2P, 6)
            addresses += self.node_manager.get_random_addresses(NetworkType.CJDNS, 6)
            return jsonify(addresses), 200

        @self.app.route("/nodes/ipv4", methods=["GET"])
        def get_ipv4_nodes():
            """Get reachable IPv4 nodes."""
            addresses = self.node_manager.get_random_addresses(NetworkType.IPV4, 32)
            return jsonify(addresses), 200

        @self.app.route("/nodes/ipv6", methods=["GET"])
        def get_ipv6_nodes():
            """Get reachable IPv6 nodes."""
            addresses = self.node_manager.get_random_addresses(NetworkType.IPV6, 32)
            return jsonify(addresses), 200

        @self.app.route("/nodes/onion", methods=["GET"])
        def get_onion_nodes():
            """Get reachable Onion nodes."""
            addresses = self.node_manager.get_random_addresses(NetworkType.ONION_V3, 32)
            return jsonify(addresses), 200

        @self.app.route("/nodes/i2p", methods=["GET"])
        def get_i2p_nodes():
            """Get reachable I2P nodes."""
            addresses = self.node_manager.get_random_addresses(NetworkType.I2P, 32)
            return jsonify(addresses), 200

        @self.app.route("/nodes/cjdns", methods=["GET"])
        def get_cjdns_nodes():
            """Get reachable CJDNS nodes."""
            addresses = self.node_manager.get_random_addresses(NetworkType.CJDNS, 32)
            return jsonify(addresses), 200

    def start(self):
        """Start REST server thread."""
        self.server_thread = Thread(
            target=self.app.run, kwargs={"host": self.address, "port": self.port}
        )
        self.server_thread.start()
        log.info("Started RESTServer on %s:%d.", self.address, self.port)
