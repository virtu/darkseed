"""Module for darkdig cli."""

from .config import DNSConfig as DarkseedDNSConfig
from .darkseed import main

__all__ = ["main", "DarkseedDNSConfig"]
