# darkseed

A proof-of-concept darknet Bitcoin DNS seeder.

`darkseed` can advertise Onion, I2P and CJDNS node addresses using custom-encoded DNS
AAAA records which use a BIP155-like format (essentially BIP155 sans timestamp and
port). Although CJDNS addresses could be represented using regular AAAA records, for the
time being they use the BIP155-like encoding to make them easily distinguishable from
regular IPv6 addresses.

`darkseed` can serve this data over the IP, Onion, I2P and Cjdns networks. To provide
reachability via Onion and I2P, the seeder supports DNS via TCP; Cjdns is handled via
regular DNS via UDP. Consequently, `darkseed` can help bootstrap darknet Bitcoin nodes
by providing them with darknet peers without exiting the darknet.

## Components

### darkdig

Tool to send DNS queries and decode `darkseed`'s custom-encoded DNS AAAA records.

`darkseed` will answer the A, AAAA, and ANY queries sent to the base domain with IPv4,
IPv6, and a mix of IPv4/IPv6 addresses, respectively.

Particular addresses types can be queried via subdomains, which use a similar format as
the `x` subdomain used to query for particular service bits. The subdomain starts with
`n` (for network id) and is followed by the network ids defined in
[BIP155](https://github.com/bitcoin/bips/blob/master/bip-0155.mediawiki). The following
subdomains are supported:
- `n1` for IPv4 addresses
- `n2` for IPv6 addresses
- `n4` for TorV3 addresses
- `n5` for I2P addresses
- `n6` for CJDNS addresses

Yggdrasil (`0x07`) and deprecated TorV2 (`0x03`) are not supported.

Example:

TODO

```bash
darkdig --type ANY dnsseed.21.ninja
; <<>> darkdig 0.11.0 <<>> @185.12.64.1 -p 53 dnsseed.21.ninja
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 21953
;; flags: qr rd ra, QUERY: 1, ANSWER: 3, AUTHORITY: 0, ADDITIONAL: 0

;;QUESTION SECTION:
; domain=dnsseed.21.ninja., rdclass=IN, rdtype=ANY

;;ANSWER SECTION:
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=168.119.72.213
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=71.56.178.136
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=120.226.39.100
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=198.98.117.238
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=216.41.130.41
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=109.145.44.244
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=75.119.148.111
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=104.193.198.210
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=80.79.5.152
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=80.108.219.153
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a13:4ac0:10:0:f816:3eff:febe:72a5
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2600:1f18:66fc:d700:9b71:f45:f3c9:c43b
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a01:4f8:13b:3692::2
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a01:e0a:b5:7f50:c257:a55b:4846:97e1
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=NULL
;; ->>custom NULL encoding<<- size: 167, records: 6, data (base64): BgQ6cwf3BI5e0OTATsTwpSjkQHibwghQieD3YQ7mG7kfugRAc5QoBdpw86fvfx/U2GrRCiL5MsguL81A/QZUumNolwVoWIU1a6BMXVSwSrWULGnlgxbUNv/nV/CX2rmx0sFgLgU3XDZWCzYqsNL6MWKFDJH+9/NDk8Txs9vnGjtAwf/UDQb8oAFReayJkrUevcRu2UG+BvyVbtuvZZ6jzSch7/XiKcY
;; ->>custom NULL-encoded address <<- record: 0, net_type: onion_v3, address: hjzqp5yerzpnbzgaj3cpbjji4rahrg6cbbiityhxmehomg5zd65fx5id.onion
;; ->>custom NULL-encoded address <<- record: 1, net_type: onion_v3, address: ibzzikaf3jyphj7pp4p5jwdk2efcf6jszaxc7tka7udfjotdnclukuad.onion
;; ->>custom NULL-encoded address <<- record: 2, net_type: i2p, address: nbmiknllubgf2vfqjk2zildj4wbrnvbw77tvp4ex3k43duwbmaxa.b32.i2p
;; ->>custom NULL-encoded address <<- record: 3, net_type: i2p, address: g5odmvqlgyvlbux2gfrikder7337gq4tyty3hw7hdi5ubqp72qgq.b32.i2p
;; ->>custom NULL-encoded address <<- record: 4, net_type: cjdns, address: fca0:151:79ac:8992:b51e:bdc4:6ed9:41be
;; ->>custom NULL-encoded address <<- record: 5, net_type: cjdns, address: fc95:6edb:af65:9ea3:cd27:21ef:f5e2:29c6

;; Query time: 501 msec
;; SERVER: 185.12.64.1#53
;; WHEN: Thu Sep 05 07:54:16 CEST 2024
;; MSG SIZE  rcvd: 485
```

NOTE: The repository contains a Nix flake so to test without installing use `nix
shell . -c darkdig dnsseed.21.ninja`

You can also use regular `dig` to query the server, although this means the NULL record
won't be decoded:

```bash
dig ANY x4.dnsseed.21.ninja

; <<>> DiG 9.18.20 <<>> ANY dnsseed.21.ninja
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 15743
;; flags: qr rd ra; QUERY: 1, ANSWER: 15, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
;; QUESTION SECTION:
;dnsseed.21.ninja.    IN  ANY

;; ANSWER SECTION:
dnsseed.21.ninja. 60  IN  A 216.121.186.10
dnsseed.21.ninja. 60  IN  A 185.205.124.79
dnsseed.21.ninja. 60  IN  A 79.239.226.41
dnsseed.21.ninja. 60  IN  A 88.71.79.122
dnsseed.21.ninja. 60  IN  A 65.108.72.50
dnsseed.21.ninja. 60  IN  A 90.76.125.121
dnsseed.21.ninja. 60  IN  A 136.32.241.190
dnsseed.21.ninja. 60  IN  A 93.123.180.164
dnsseed.21.ninja. 60  IN  A 199.85.210.133
dnsseed.21.ninja. 60  IN  A 144.2.121.100
dnsseed.21.ninja. 60  IN  AAAA  2001:f40:94e:7ff:7270:fcff:fe05:3cd
dnsseed.21.ninja. 60  IN  AAAA  2a03:4000:6:162d::1
dnsseed.21.ninja. 60  IN  AAAA  2a01:4f8:202:3e6::2
dnsseed.21.ninja. 60  IN  AAAA  2a10:3781:3a73:25:a177:ad25:b14a:176a
dnsseed.21.ninja. 60  IN  NULL  \# 167 060432D092A38189F7986AF56E71D3020A415C225118CE098209C91A E04FF5B6712604FC9BEFA1C1B056A62F841E568A43220DBAF0263EFB 497C7826FCFC83C8F9D43105B61A77223CDE421DD1CF5B3687615AE6 D157F3B6FEC4F834CB333A705BE767260592DACA4C9D778FADAC6866 F968BB993F200D3C476C94C1BC8AD3722FD3AECFD306FC322C16D0D0 F1FB3B27C1878CB5920106FCC7BE49CCD1DC913125F0DA457D08CE

;; Query time: 28 msec
;; SERVER: 185.12.64.1#53(185.12.64.1) (TCP)
;; WHEN: Thu Sep 05 07:56:31 CEST 2024
;; MSG SIZE  rcvd: 496
```

## Local Testing (with Nix)

Make sure to make reachable node data (generated with `p2p-crawler`) available in a
`node_data` directory under the git repository root.

```bash
# Start a darkseed instance serving nodes via DNS on port 8053
nix run . -- --log-level debug --crawler-path $(git rev-parse --show-toplevel)/test_data --port 8053 --zone seed.acme.com

# Test
nix shell . -c darkdig seed.acme.com --nameserver 127.0.0.1 -p 8053
```
