# darkseed

A proof-of-concept darknet Bitcoin DNS seeder.

`darkseed` can advertise Onion, I2P and CJDNS node addresses using custom DNS NULL
records in which addresses are encoded using a BIP155-like format (essentially BIP155
sans timestamp and port). Although CJDNS addresses could be represented using regular
AAAA records, for the time being they use the BIP155-like encoding to make them easily
distinguishable from regular IPv6 addresses.

`darkseed` can serve this data over the IP, Onion, I2P and Cjdns networks. To provide
reachability via Onion and I2P, the seeder supports DNS via TCP; Cjdns is handled via
regular DNS via UDP. Consequently, `darkseed` can help bootstrap darknet Bitcoin nodes
by providing them with darknet peers without exiting the darknet.

## Components

### darkdig

Tool to query a DNS peer and decode custom DNS NULL records used by `darkseed`.

The ANY query type will return a mix of clearnet and darknet addresses. The A, AAAA and
NULL query types will respectively return IPv4, IPv6 and darknet addresses exclusively.

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
```bash
dig ANY dnsseed.21.ninja

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

## Darknet availability (Tor, I2P and Cjdns)

A demo instance of `darkseed` is reachable via TOR, I2P and Cjdns.

Unfortunately I haven't found a way to integrate Onion and I2P addresses in DNS NS
records, so nameservers have to be specified manually for now.

NOTE: Due to shenanigans with DNS (DOS attacks where attackers spoof UDP source IPs in
small DNS packets to overwhelm a target with large replies), the demo `darkseed`
instance is rate limited to five requests per minute using `fail2ban` with a ban time of
one hour.

### Tor

Instances are reachable under the following addresses:
- `qhhxx7a2fcbzk2p2bj257c7uhrjorzhnyefuo34epmm3vlooqwemfmad.onion`
- `d4natwynl7lqkkklzsiw4is2esztijy54v77vjfqqrmwkucm3ygjlcyd.onion`

Since Tor does not support UDP, the DNS query must be sent via TCP. This is done using
the Tor Socks5 proxy, which is reachable via `localhost:9050` by default. Note that
depending on distribution, the proxy might or might not be enabled by default when using
Tor (for NixOS, simply set `darkseed.client.enable` = true).

Example:

```bash
darkdig dnsseed.21.ninja. --type ANY --nameserver qhhxx7a2fcbzk2p2bj257c7uhrjorzhnyefuo34epmm3vlooqwemfmad.onion --socks5-proxy 127.0.0.1:9050 --tcp

; <<>> darkdig 0.11.0 <<>> @qhhxx7a2fcbzk2p2bj257c7uhrjorzhnyefuo34epmm3vlooqwemfmad.onion -p 53 --socks5-proxy 127.0.0.1:9050 --tcp dnsseed.21.ninja.
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 54269
;; flags: qr rd, QUERY: 1, ANSWER: 3, AUTHORITY: 0, ADDITIONAL: 0

;;QUESTION SECTION:
; domain=dnsseed.21.ninja., rdclass=IN, rdtype=ANY

;;ANSWER SECTION:
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=144.91.115.96
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=34.97.134.215
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=24.220.72.43
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=37.63.53.45
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=195.201.28.201
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=104.155.87.142
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=136.34.197.3
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=188.166.102.98
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=66.130.255.242
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=158.220.97.83
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2401:4900:1c97:b147:2460:2e:3cbb:dcde
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2600:3c01::f03c:91ff:fed8:db38
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a01:4f9:2a:19a7::2
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2002:c338:3f0c::c338:3f0c
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=NULL
;; ->>custom NULL encoding<<- size: 167, records: 6, data (base64): BgRlWurDygz2eTXWy2nv3jdmFhwR3dPZ7qFdiMP8RfcIDAQXj4qpTY9vFs+3uO/Euk+aLCo2FNsBzD6+nnQtXYxRawVHBEC8rkEA/H6Xbj8U1bn6V/jCvdyKswO8eB6+QwJfyAWSBVu1voQ9Bp/nZ/iGMZdKFDG/6t8sFVNCRBwnOYP6rwb8bfVihqB5HYogeqKIeSF2Bvxw3p1/4gsyWCgaPA0Pg+w
;; ->>custom NULL-encoded address <<- record: 0, net_type: onion_v3, address: mvnovq6kbt3hsnowznu67xrxmylbyeo52pm65ik5rdb7yrpxbagcubyd.onion
;; ->>custom NULL-encoded address <<- record: 1, net_type: onion_v3, address: c6hyvkknr5xrnt5xxdx4josptiwcunqu3ma4ypv6tz2c2xmmkfv5ghid.onion
;; ->>custom NULL-encoded address <<- record: 2, net_type: i2p, address: i4cebpfoieapy7uxny7rjvnz7jl7rqv53sflga54papl4qycl7ea.b32.i2p
;; ->>custom NULL-encoded address <<- record: 3, net_type: i2p, address: sicvxnn6qq6qnh7hm74immmxjikddp7k34wbku2ciqocoomd7kxq.b32.i2p
;; ->>custom NULL-encoded address <<- record: 4, net_type: cjdns, address: fc6d:f562:86a0:791d:8a20:7aa2:8879:2176
;; ->>custom NULL-encoded address <<- record: 5, net_type: cjdns, address: fc70:de9d:7fe2:b32:5828:1a3c:d0f:83ec

;; Query time: 3441 msec
;; SERVER: qhhxx7a2fcbzk2p2bj257c7uhrjorzhnyefuo34epmm3vlooqwemfmad.onion#53
;; WHEN: Thu Sep 05 08:00:51 CEST 2024
;; MSG SIZE  rcvd: 485
```

### I2P

Instances are reachable under the following addresses:
- `4ibvyflekkqc45domfbdlfp7zudurmd7x6whd4x5q7vsor7sgwtq.b32.i2p`
- `ja7o42qnralhke5kwsatycm7hj4ssq6gqwdrcsjvgt3xe3a2tvga.b32.i2p`

Since I2P does not support UDP, the DNS query must be sent via TCP. This is done using
the Onion Socks5 proxy, which is reachable via `localhost:4447` by default. Note that
depending on distribution, the proxy might or might not be enabled by default when using
I2P (for NixOS, simply set `darkseed.client.enable` = true).

Example:

```bash
darkdig dnsseed.21.ninja. --type ANY --nameserver 4ibvyflekkqc45domfbdlfp7zudurmd7x6whd4x5q7vsor7sgwtq.b32.i2p --socks5-proxy 127.0.0.1:4447 --tcp
; <<>> darkdig 0.11.0 <<>> @4ibvyflekkqc45domfbdlfp7zudurmd7x6whd4x5q7vsor7sgwtq.b32.i2p -p 53 --socks5-proxy 127.0.0.1:4447 --tcp dnsseed.21.ninja.
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 24448
;; flags: qr rd, QUERY: 1, ANSWER: 3, AUTHORITY: 0, ADDITIONAL: 0

;;QUESTION SECTION:
; domain=dnsseed.21.ninja., rdclass=IN, rdtype=ANY

;;ANSWER SECTION:
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=8.217.206.230
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=50.102.2.188
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=34.74.24.33
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=154.26.159.203
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=34.96.182.63
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=54.146.220.99
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=13.229.129.207
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=171.97.235.226
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=87.209.21.41
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=219.79.200.233
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a01:4f8:2190:2cc4::2
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a01:4f9:2b:29a::2
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2604:a880:cad:d0::d8c:d001
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a03:b0c0:1:e0::397:6001
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=NULL
;; ->>custom NULL encoding<<- size: 167, records: 6, data (base64): BgRc/X1v3rrgYQmNl5mhyefwTsyC+C3HHBzAoUqc/ZeEJwShr1fgbGyB51MlotovQlTk/EPjI5h+Uy+crrkDS4KmaQVlM+GuwFjQAMWV4ZyIubFREzSgCKzf2XLY5dCp2psqIwUFAJnDJJU77Xg1ev7qXb+Fc5fdFSv3XQeCuP0c2xj8Pgb8lW7br2Weo80nIe/14inGBvzHvknM0dyRMSXw2kV9CM4
;; ->>custom NULL-encoded address <<- record: 0, net_type: onion_v3, address: lt6x2366xlqgccmns6m2dsph6bhmzaxyfxdryhgauffjz7mxqqtr4tad.onion
;; ->>custom NULL-encoded address <<- record: 1, net_type: onion_v3, address: ugxvpydmnsa6ouzfulnc6qsu4t6ehyzdtb7fgl44v24qgs4cuzuxucqd.onion
;; ->>custom NULL-encoded address <<- record: 2, net_type: i2p, address: muz6dlwaldiabrmv4goironrkejtjiaivtp5s4wy4xiktwu3firq.b32.i2p
;; ->>custom NULL-encoded address <<- record: 3, net_type: i2p, address: auajtqzesu5626bvpl7ouxn7qvzzpxivfp3v2b4cxd6rzwyy7q7a.b32.i2p
;; ->>custom NULL-encoded address <<- record: 4, net_type: cjdns, address: fc95:6edb:af65:9ea3:cd27:21ef:f5e2:29c6
;; ->>custom NULL-encoded address <<- record: 5, net_type: cjdns, address: fcc7:be49:ccd1:dc91:3125:f0da:457d:8ce

;; Query time: 2570 msec
;; SERVER: 4ibvyflekkqc45domfbdlfp7zudurmd7x6whd4x5q7vsor7sgwtq.b32.i2p#53
;; WHEN: Thu Sep 05 08:05:04 CEST 2024
;; MSG SIZE  rcvd: 485
```

### Cjdns

Instances are reachable under the following addresses:
- `fcf9:45bc:8c48:6973:7b3f:5538:6e51:8fc9`
- `fc1f:3640:c8e1:af7:d177:f6c9:e443:6fdf`

Cjdns works transparently and supports UDP, so no proxy and DNS over TCP is required.

Example:

```bash
darkdig dnsseed.21.ninja. --type ANY --nameserver fcf9:45bc:8c48:6973:7b3f:5538:6e51:8fc9
; <<>> darkdig 0.11.0 <<>> @fcf9:45bc:8c48:6973:7b3f:5538:6e51:8fc9 -p 53 dnsseed.21.ninja.
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 2091
;; flags: qr rd, QUERY: 1, ANSWER: 3, AUTHORITY: 0, ADDITIONAL: 0

;;QUESTION SECTION:
; domain=dnsseed.21.ninja., rdclass=IN, rdtype=ANY

;;ANSWER SECTION:
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=60.205.205.119
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=108.35.247.78
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=65.21.22.132
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=141.98.153.137
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=54.202.35.84
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=203.11.72.11
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=45.90.57.143
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=72.133.177.119
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=217.162.57.192
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=92.39.195.153
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a01:4f8:c2c:a951::1
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2607:fea8:601e:7d01:be24:11ff:fe89:27f3
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a01:4f8:1c1c:a0a6::1
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a02:1210:4c5e:5a00:d450:529b:13b6:173
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=NULL
;; ->>custom NULL encoding<<- size: 167, records: 6, data (base64): BgS4WazO56P8gMge/e0fsmLdWkE5BiOkHW017vD82LK3SAS2GX9uBEvUzk0K5hMQAeaqlS7Q/JaIj231jl/an78hhAXgUQRBNi8SZFeX8wuKxab5GDqUtUhjM8gIk+YRJz0vqwXFlRiHGbGF0Ol0DxHc9RaZBlzoODHP/u65XHi7yVaMmwb8lW7br2Weo80nIe/14inGBvzLAkgRphBCC8oSGPfOfT0
;; ->>custom NULL-encoded address <<- record: 0, net_type: onion_v3, address: xbm2ztxhup6ibsa67xwr7mtc3vnecoigeosb23jv53ypzwfsw5eaprid.onion
;; ->>custom NULL-encoded address <<- record: 1, net_type: onion_v3, address: wymx63qejpkm4tik4yjraapgvkks5uh4s2ei63pvrzp5vh57egcb2oyd.onion
;; ->>custom NULL-encoded address <<- record: 2, net_type: i2p, address: 4biqiqjwf4jgiv4x6mfyvrng7emdvffvjbrthsaisptbcjz5f6vq.b32.i2p
;; ->>custom NULL-encoded address <<- record: 3, net_type: i2p, address: ywkrrbyzwgc5b2lub4i5z5iwtedfz2byghh753vzlr4lxskwrsnq.b32.i2p
;; ->>custom NULL-encoded address <<- record: 4, net_type: cjdns, address: fc95:6edb:af65:9ea3:cd27:21ef:f5e2:29c6
;; ->>custom NULL-encoded address <<- record: 5, net_type: cjdns, address: fccb:248:11a6:1042:bca:1218:f7ce:7d3d

;; Query time: 206 msec
;; SERVER: fcf9:45bc:8c48:6973:7b3f:5538:6e51:8fc9#53
;; WHEN: Thu Sep 05 08:06:59 CEST 2024
;; MSG SIZE  rcvd: 485
```

## Hints

To test the darknet availability of one's own `darkseed` instance, the following might
be helpful.

On NixOS, a `darkseed` instance's
- Onion address can be found in the file `/var/lib/tor/onion/darkseed/hostname`
- I2P address can be derived by appending `.b32.i2p` to the result of `sudo head -c 391
  /var/lib/i2pd/darkseed-keys.dat | sha256sum | cut -f1 -d\  | xxd -r -p | base32 | tr
  '[:upper:]' '[:lower:]' | sed -r 's/=//g'`
- Cjdns address is associated with the `tun0` interface (`ip -6 addr show dev tun0 | awk
  '/inet6/ && /global/ {print $2; exit}' | cut -d'/' -f1`)
