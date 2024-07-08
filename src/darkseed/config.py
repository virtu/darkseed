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
    crawler_path: Path
    ttl: int

    @classmethod
    def parse(cls, args):
        """Create class instance from arguments."""

        return cls(
            version=__version__,
            timestamp=args.timestamp,
            log_level=args.log_level.upper(),
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
