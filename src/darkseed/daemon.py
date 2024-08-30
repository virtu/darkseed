"""Darkseed daemon that listens for DNS requests and commands."""

import logging as log
import socketserver
import sys
import threading
import time

from darkseed.config import get_config
from darkseed.dns import DNSServer
from darkseed.node_manager import NodeManager
from darkseed.rest import RESTServer


class CommandServerHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip().decode("utf-8")
        log.debug("Command received: %s", data)
        response = ""
        if data.lower() == "status":
            response = "Server running. Uptime: 100 minutes."
        elif data.lower() == "update":
            response = "Updated records."
        else:
            response = "Invalid command."

        self.request.sendall(response.encode("utf-8"))


def start_command_server():
    server = socketserver.TCPServer(("localhost", 8054), CommandServerHandler)
    log.info("Started CommandServer thread.")
    server.serve_forever()


def main():
    """Parse command-line arguments, set up logging, and run darkseed daemon."""

    conf = get_config()
    log.basicConfig(
        level=conf.log_level,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    log.Formatter.converter = time.gmtime
    log.info("Using configuration: %s", conf)

    command_thread = threading.Thread(target=start_command_server)
    command_thread.start()

    node_manager = NodeManager(conf.crawler_path)
    node_manager.start()

    dns_server = DNSServer(conf.dns_address, conf.dns_port, node_manager)
    dns_server.start()

    rest_server = RESTServer(conf.rest_address, conf.rest_port, node_manager)
    rest_server.start()


if __name__ == "__main__":
    main()
