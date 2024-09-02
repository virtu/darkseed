"""Darkseed daemon that listens for DNS requests and commands."""

import logging as log
import time

from darkseed.config import get_config
from darkseed.dns import DNSServer
from darkseed.node_manager import NodeManager
from darkseed.rest import RESTServer


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

    node_manager = NodeManager(conf.crawler_path)
    node_manager.start()

    dns_server = DNSServer(conf.dns, node_manager)
    dns_server.start()

    rest_server = RESTServer(conf.rest_address, conf.rest_port, node_manager)
    rest_server.start()


if __name__ == "__main__":
    main()
