"""Module containing classes for node services."""

from enum import IntFlag


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
