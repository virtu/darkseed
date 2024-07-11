"""Module for the Node class."""

from functools import cached_property

from .address import Address


class Node:
    """Class representing a Bitcoin node."""

    def __init__(self, address: str, port: int, services: int):
        self.address = Address(address)
        self.port = port
        self.services = services

    @cached_property
    def net_type(self):
        """Get node's network type from address."""
        return self.address.net_type

    def has_services(self, services: int) -> bool:
        """Check if the node has the required services enabled."""
        return self.services & services == services
