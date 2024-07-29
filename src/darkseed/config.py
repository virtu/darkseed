"""Configuration options for darkseed daemon."""

import argparse
import datetime
import importlib.metadata
import os
from dataclasses import asdict, dataclass
from pathlib import Path

__version__ = importlib.metadata.version(__package__ or __name__)


@dataclass
class Config:
    """Configuration settings for the daemon."""

    version: str
    timestamp: datetime.datetime
    log_level: str
    dns_address: str
    dns_port: int
    rest_address: str
    rest_port: int
    crawler_path: Path
    ttl: int

    @classmethod
    def parse(cls, args):
        """Create class instance from arguments."""

        return cls(
            version=__version__,
            timestamp=args.timestamp,
            log_level=args.log_level.upper(),
            dns_address=args.dns_address,
            dns_port=args.dns_port,
            rest_address=args.rest_address,
            rest_port=args.rest_port,
            crawler_path=args.crawler_path,
            ttl=args.ttl,
        )

    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)


def parse_args():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--log-level",
        type=str,
        default=os.environ.get("LOG_LEVEL", "INFO"),
        help="Logging verbosity",
    )

    parser.add_argument(
        "--crawler-path",
        type=Path,
        default="/home/p2p-crawler/",
        help="Directory containing data created by p2p-crawler",
    )

    parser.add_argument(
        "--ttl",
        type=int,
        default=60,
        help="TTL for DNS records (in seconds)",
    )

    parser.add_argument(
        "--dns-address",
        type=str,
        default="127.0.0.1",
        help="IP address used by the DNS server",
    )

    parser.add_argument(
        "--dns-port",
        type=int,
        default=53,
        help="UDP port used by the DNS server",
    )

    parser.add_argument(
        "--rest-address",
        type=str,
        default="127.0.0.1",
        help="IP address used by the REST server",
    )

    parser.add_argument(
        "--rest-port",
        type=int,
        default=80,
        help="UDP port used by the REST server",
    )

    parser.add_argument(
        "--timestamp",
        default=datetime.datetime.utcnow(),
        help="Set custom timestamp when daemon was started",
    )
    args = parser.parse_args()

    return args


def get_config():
    """Parse command-line arguments and get configuration settings."""

    args = parse_args()
    conf = Config.parse(args)
    return conf
