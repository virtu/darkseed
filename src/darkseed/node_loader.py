"""Module for handling reachable nodes data."""

import bz2
import csv
import logging as log
import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import ClassVar

from darkseed.dns import dns_responder
from darkseed.node import Node


@dataclass(unsafe_hash=True)
class NodeLoader(threading.Thread):
    """Class that provides reachable nodes data."""

    path: Path
    refresh: int = 600  # refresh frequency in seconds. default: ten minutes
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
        counter = defaultdict(int)
        with bz2.open(data_file, "rt") as file:
            reader = csv.DictReader(file)  # type: ignore
            rows = list(reader)
        for row in rows:
            counter["total"] += 1
            net, port = row["network"], int(row["port"])
            if (net != "i2p" and port != NodeLoader.MAINNET_PORT) or (
                net == "i2p" and port != 0
            ):
                if row["network"] == "i2p":
                    print(f"discarding i2p node with port {row['port']}")
                counter["bad_port"] += 1
                continue
            handshake = row["handshake_successful"].lower() == "true"
            if not handshake:
                counter["incomplete_handshake"] += 1
                continue
            counter["good"] += 1
            node = Node(row["host"], port, int(row["services"]))
            assert str(node.net_type) == row["network"], "Error detecting network type!"
            nodes.append(node)
        log.info(
            "Extracted %d viable nodes from %s (total=%d, bad_port=%d, incomplete_handshake=%d)",
            counter["good"],
            data_file,
            counter["total"],
            counter["bad_port"],
            counter["incomplete_handshake"],
        )
        return nodes

    def get_latest_data(self):
        """Get latest reachable nodes data."""

        data_file = self.get_latest_file()
        nodes = self.read_data_file(data_file)
        dns_responder.set_reachable_nodes(nodes)
        log.debug("Updated reachable nodes in dns_responder")
