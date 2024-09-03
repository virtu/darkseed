# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2024-09-03

- Support DNS (TCP) via I2P
  - Create I2P tunnels for darknet TCP DNS
  - Allow darkdig to use a socks5 proxy
    - Add `pysocks` as dependency
    - Add `--proxy` command-line argument to darkdig a proxy can be specified

## [0.3.0] - 2024-09-03

- Respect DNS zone
  - Add `--dns-zone` command-line argument and `darkseed.dns.zone` nix module setting
  - Refuse DNS queries that don't match configured zone
  - Use dedicated `DNSConfig` class in `config.py`
- Remove unused `CommandServer`
- Introduce [change log](CHANGELOG.md)
