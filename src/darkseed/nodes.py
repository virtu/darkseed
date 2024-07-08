"""Module for handling reachable nodes data."""

import bz2
import csv
import logging as log
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import ClassVar

from darkseed.dns import NodeAddress, dns_request_handler


@dataclass(unsafe_hash=True)
class NodeProvider(threading.Thread):
    """Class that provides reachable nodes data."""

    path: Path
    refresh: int = 3600  # refresh frequency in seconds
    MAINNET_PORT: ClassVar[int] = 8333

    def __post_init__(self):
        super().__init__(name=self.__class__.__name__)

    def run(self):
        self.get_latest_data()

        log.debug("Sleeping for %d seconds", self.refresh)
        time.sleep(self.refresh)
        self.get_latest_data()
        log.debug("Waking after %d seconds", self.refresh)

    def get_latest_file(self):
        """Get latest reachable nodes file."""
        log.debug("Attempting to fetch reachable node data from %s", self.path)
        node_files = self.path.glob("*_reachable_nodes.csv.bz2")

        def get_timestamp(file):
            timestamp_str = file.name.split("_")[0]
            return datetime.strptime(timestamp_str, "%Y-%m-%dT%H-%M-%SZ")

        latest_file = max(node_files, key=get_timestamp, default=None)
        if not latest_file:
            raise ValueError(f"No crawler data found in {self.path}!")
        return latest_file

    @staticmethod
    def read_data_file(data_file):
        """Read bz2-compressed crawler data, filter nodes using a non-standard port, output statistics."""
        nodes = []
        with bz2.open(data_file, "rt") as file:
            reader = csv.DictReader(file)  # type: ignore
            for row in reader:
                nodes.append(NodeAddress(row["host"], int(row["port"]), row["network"]))
        num_total = len(nodes)
        nodes = [n for n in nodes if n.port == NodeProvider.MAINNET_PORT]
        num_good = len(nodes)
        num_bad = num_total - num_good
        log.info(
            "Read %d nodes from %s: ipv4=%d, ipv6=%d, onion=%d, i2p=%d, cjdns=%d (good=%d, bad_port=%d)",
            num_total,
            data_file,
            len([n for n in nodes if n.network == "ipv4"]),
            len([n for n in nodes if n.network == "ipv6"]),
            len([n for n in nodes if n.network == "onion_v3"]),
            len([n for n in nodes if n.network == "i2p"]),
            len([n for n in nodes if n.network == "cjdns"]),
            num_good,
            num_bad,
        )
        return nodes

    def get_latest_data(self):
        """Get latest reachable nodes data."""

        data_file = self.get_latest_file()
        nodes = self.read_data_file(data_file)
        log.debug("Setting reachable nodes in dns_request_handler")
        dns_request_handler.set_reachable_nodes(nodes)
        log.debug("Set reachable nodes in dns_request_handler")
