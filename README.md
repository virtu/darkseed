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

#### Example

```bash
darkdig --type AAAA n4.dnsseed.21.ninja

; <<>> darkdig 0.13 <<>> @192.168.178.1 -p 53 -l INFO n4.dnsseed.21.ninja
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 13738
;; flags: qr rd ra, QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

;;QUESTION SECTION:
; domain=n4.dnsseed.21.ninja., rdclass=IN, rdtype=AAAA

;;ANSWER SECTION:
domain=n4.dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc0e:3854:4700::
domain=n4.dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc0c:a113:277b:8ff9:1907:8e03:b934:c4b9
domain=n4.dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc00:604:1070:cbfe:535b:2114:e03f:bfe0
domain=n4.dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc0b:bf41:594e:81af:422f:548a:ca77:4ff
domain=n4.dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc09:27b:4555:da65:1004:87b2:db4d:a55b
domain=n4.dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc08:5fcf:75f8:61e6:88f3:42e7:eb5f:4116
domain=n4.dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc05:4481:9e78:3fda:b3ef:ec3e:6a99:4e14
domain=n4.dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc03:1b2c:aad4:a5b4:95be:63c6:3dc8:eea3
domain=n4.dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc06:322b:33eb:305a:e1da:6cc9:6dfa:4b1d
domain=n4.dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc07:1d56:471:e890:3b08:b458:c0e0:d33a
domain=n4.dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc02:897a:964:1be6:426:1d94:5830:a481
domain=n4.dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc01:6dd3:3743:bcd3:b255:a44d:2f41:4088
domain=n4.dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc04:da30:9f01:1e18:1a9f:da06:a104:c159
domain=n4.dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc0a:fb6e:3c6d:8ef6:c438:a6e6:f96a:68e
domain=n4.dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc0d:1639:6d34:1026:ae6:73b:7dbd:80cb
;; ->>custom AAAA encoding<<-
;; ->>custom AAAA-encoded address <<- record: 0, net_type: onion_v3, address: cbymx7stlmqrjyb7x7qg3uzxio6nhmsvurgs6qkarcexucledptbtiad.onion
;; ->>custom AAAA-encoded address <<- record: 1, net_type: onion_v3, address: eyoziwbqusarwlfk2ss3jfn6mpdd3shoupndbhybdymbvh62a2qzjnid.onion
;; ->>custom AAAA-encoded address <<- record: 2, net_type: onion_v3, address: yfmujam6pa75vm7p5q7gvgkocqzcwm7lgbnodwtmzfw7usy5dvlgqyqd.onion
;; ->>custom AAAA-encoded address <<- record: 3, net_type: onion_v3, address: ohujaoyiwrmmbygthjp465pymhtir42c47vv6qiwaj5ukvo2muikqnad.onion
;; ->>custom AAAA-encoded address <<- record: 4, net_type: onion_v3, address: q6znwtnflp5w4pdnr33miofg434wubuox5avstubv5bc6vekzj3zssqd.onion
;; ->>custom AAAA-encoded address <<- record: 5, net_type: onion_v3, address: 76qrgj33r74rsb4oao4tjrfzcy4w2naqeyfombz3pw6ybszykrdrfyad.onion

;; Query time: 100 msec
;; SERVER: 192.168.178.1#53
;; WHEN: Tue Oct 08 14:10:05 CEST 2024
;; MSG SIZE  rcvd: 457
```

NOTE: The repository contains a Nix flake so to test without installing use `nix
shell . -c darkdig dnsseed.21.ninja`

You can also use regular `dig` to query the server, although this means the NULL record
won't be decoded:

```bash
dig AAAA n4.dnsseed.21.ninja

; <<>> DiG 9.10.6 <<>> AAAA n4.dnsseed.21.ninja
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 57127
;; flags: qr rd ra; QUERY: 1, ANSWER: 15, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;n4.dnsseed.21.ninja.           IN      AAAA

;; ANSWER SECTION:
n4.dnsseed.21.ninja.    60      IN      AAAA    fc04:472e:e536:8b03:437b:f23c:2804:ee50
n4.dnsseed.21.ninja.    60      IN      AAAA    fc0b:ae5f:8747:4486:1c84:c924:b438:4e7
n4.dnsseed.21.ninja.    60      IN      AAAA    fc08:b50:7b9f:47b6:20fb:8fe2:e4ed:e733
n4.dnsseed.21.ninja.    60      IN      AAAA    fc0d:5496:409a:68ee:5623:5ca8:7559:c69
n4.dnsseed.21.ninja.    60      IN      AAAA    fc07:e17a:4ff:d8bb:3343:7889:d51:d64b
n4.dnsseed.21.ninja.    60      IN      AAAA    fc0a:7d1:2576:88ca:4b1b:b8c6:1226:8194
n4.dnsseed.21.ninja.    60      IN      AAAA    fc09:1bde:a8b1:7be1:d604:b177:3070:6d1
n4.dnsseed.21.ninja.    60      IN      AAAA    fc06:e6af:d1b5:37ed:a7fb:20ad:dce6:21a4
n4.dnsseed.21.ninja.    60      IN      AAAA    fc05:471b:b962:4636:c9ee:76b3:d5b9:7f9
n4.dnsseed.21.ninja.    60      IN      AAAA    fc0c:1895:3126:8e3c:bc46:f8a9:e18:e5fb
n4.dnsseed.21.ninja.    60      IN      AAAA    fc01:5881:ff18:a1fe:f697:1800:517e:f4a6
n4.dnsseed.21.ninja.    60      IN      AAAA    fc03:bc43:9214:5870:3b37:f045:3f8e:2df7
n4.dnsseed.21.ninja.    60      IN      AAAA    fc00:604:4b0a:6f82:d4a5:b37f:4a49:6969
n4.dnsseed.21.ninja.    60      IN      AAAA    fc02:d61b:35e7:ac78:422:5973:5cf9:bf4a
n4.dnsseed.21.ninja.    60      IN      AAAA    fc0e:f3b8:5200::

;; Query time: 65 msec
;; SERVER: 192.168.178.1#53(192.168.178.1)
;; WHEN: Tue Oct 08 15:05:35 CEST 2024
;; MSG SIZE  rcvd: 468
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
