# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.11.1] - 2024-09-05

- Improve file layout

## [0.11.0] - 2024-09-05

- Use BIP155-like encoding for darknet addresses in NULL records
- Also encode CJDNS addresses to avoid confusing unaware clients with AAAA records that
  aren't regular IPv6 addresses
- Update `darkdig` output in README

## [0.10.0] - 2024-09-04

- Deprecate REST support

## [0.9.1] - 2024-09-04

- Fix bug where old node data was unnecessarily loaded

## [0.9.0] - 2024-09-04

- Rate limit requests to five per minute via `fail2ban`

## [0.8.2] - 2024-09-04

- Improve summaries in DNS requests that cause warnings

## [0.8.1] - 2024-09-04

- Change logging level of request and reply summaries to `INFO`
- Only load crawler node data when new results are found

## [0.8.0] - 2024-09-04

- Proxy DNS requests between CJDNS address and nameserver using `socat`

## [0.7.0] - 2024-09-03

- Add `darkseed.client.enable` setting
  - Adds `darkdig` to PATH
  - Enables TOR and I2P socks proxies

## [0.6.0] - 2024-09-03

- Make DNS server reachable via I2P

## [0.5.0] - 2024-09-03

- Support TCP DNS via SOCKS5
  - Allow darkdig to use a socks5 proxy
    - Add `pysocks` as dependency
    - Add `--proxy` command-line argument to darkdig a proxy can be specified

## [0.4.0] - 2024-09-03

- Add `darkdig` to PATH when using NixOS module

## [0.3.0] - 2024-09-03

- Respect DNS zone
  - Add `--dns-zone` command-line argument and `darkseed.dns.zone` nix module setting
  - Refuse DNS queries that don't match configured zone
  - Use dedicated `DNSConfig` class in `config.py`
- Remove unused `CommandServer`
- Introduce [change log](CHANGELOG.md)
