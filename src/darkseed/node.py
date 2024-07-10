"""Module for the Node class."""

from dataclasses import dataclass
from enum import IntFlag

from darkseed.address import Address


class Services(IntFlag):
    """Class representing the services a node can provide."""

    NODE_NONE = 0
    NODE_NETWORK = 1 << 0
    NODE_BLOOM = 1 << 2
    NODE_WITNESS = 1 << 3
    NODE_COMPACT_FILTERS = 1 << 6
    NODE_NETWORK_LIMITED = 1 << 10
    NODE_P2P_V2 = 1 << 11
    SEEDS_SERVICES = NODE_NETWORK | NODE_WITNESS


@dataclass
class Node:
    """Class representing a Bitcoin node."""

    address: Address
    port: int
    services: int

    def has_services(self, services: int) -> bool:
        """Check if the node has the required services enabled."""
        return self.services & services == services
