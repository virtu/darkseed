"""Configuration options for darkdig CLI tool."""

import argparse
from dataclasses import asdict, dataclass


@dataclass
class Config:
    """Configuration settings."""

    verbose: bool
    domain: str
    nameserver: str
    port: int

    @classmethod
    def parse(cls, args):
        """Create class instance from arguments."""

        return cls(
            verbose=args.verbose,
            domain=args.domain,
            nameserver=args.nameserver,
            port=args.port,
        )

    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)


def parse_args():
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Tool to decode darkseed DNS replies.")

    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="Verbose output",
    )

    parser.add_argument(
        "-n",
        "--nameserver",
        type=str,
        default="",
        help="Nameserver to use",
    )

    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=53,
        help="Nameserver port to use",
    )

    parser.add_argument("domain", type=str, help="DNS query domain")
    args = parser.parse_args()

    return args


def get_config():
    """Parse command-line arguments and get configuration settings."""

    args = parse_args()
    conf = Config.parse(args)
    return conf
