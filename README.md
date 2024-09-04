# darkseed

A proof-of-concept darknet Bitcoin DNS seeder.

`darkseed` can advertise Onion, I2P and CJDNS node
addresses using custom DNS NULL records in which addresses are encoded using a
BIP155-like format. `darkseed` can serve this data over
the IP, Onion, I2P and Cjdns networks. To provide reachability via Onion and I2P, the
seeder supports TCP via DNS; Cjdns is handled via regular TCP via UDP.

Consequently, `darkseed` can help bootstrap darknet Bitcoin nodes by providing them with
darknet peers without exiting the darknet.

## Components

### darkdig

Tool to query a DNS peer and decode custom DNS NULL records used by `darkseed`.

Example:

```bash
darkdig --type ANY dnsseed.21.ninja

; <<>> darkdig 0.10.0 <<>> @185.12.64.1 -p 53 dnsseed.21.ninja
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 57103
;; flags: qr rd ra, QUERY: 1, ANSWER: 3, AUTHORITY: 0, ADDITIONAL: 0

;;QUESTION SECTION:
; domain=dnsseed.21.ninja., rdclass=IN, rdtype=ANY

;;ANSWER SECTION:
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=190.2.140.148
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=147.135.136.53
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=86.104.228.36
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=191.13.128.58
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=103.231.42.36
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=80.67.179.144
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=46.4.119.153
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=135.181.199.179
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=162.219.38.94
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=84.75.176.110
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc32:2c16:d0d0:f1fb:3b27:c187:8cb5:9201
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a01:4f8:262:4d80::2
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a01:e0a:dec:3d50:4f87:2004:3f1d:90c7
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2600:1900:40b0:3af2:0:5::
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a01:e0a:c4d:9dd0:c58a:d613:2417:a9dc
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc95:6edb:af65:9ea3:cd27:21ef:f5e2:29c6
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=NULL
;; ->>custom NULL encoding<<- size: 133, records: 4, data (base64): BAAEXjYaYI6QymodE3FtbrqFmSB+rgybXuW53vF6vyJEOgAvsXpohUCf5JmOt981bYpOj15eG/6fpgG2Cr3KebkkjgG3yyQnPE0VNOXqkLSCC0tMx4Ua5Ik2zY7FbDM16LN2hAEOhIKDmywBsI+R6AbpKdhwb076hZqB3eJS0lhd9F+WHw
;; ->>custom NULL-encoded address <<- record: 0, address: arpdmgtar2imu2q5cnyw23v2qwmsa7vobsnv5znz33yxvpzciq5dqeid.onion
;; ->>custom NULL-encoded address <<- record: 1, address: f6yxu2eficp6jgmow7ptk3mkj2hv4xq372p2manwbk64u6nzeshozqid.onion
;; ->>custom NULL-encoded address <<- record: 2, address: w7fsijz4juktjzpksc2iec2ljtdykgxere3m3dwfnqztl2fto2ca.b32.i2p
;; ->>custom NULL-encoded address <<- record: 3, address: b2cifa43fqa3bd4r5adoskoyobxu56uftka53yss2jmf35c7sypq.b32.i2p

;; Query time: 117 msec
;; SERVER: 185.12.64.1#53
;; WHEN: Wed Sep 04 15:35:58 CEST 2024
;; MSG SIZE  rcvd: 507
```

NOTE: The repository contains a Nix flake so to test without installing use `nix
shell . -c darkdig dnsseed.21.ninja`

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

### Tor

Instances are reachable under the following addresses:
- `d4natwynl7lqkkklzsiw4is2esztijy54v77vjfqqrmwkucm3ygjlcyd.onion`
- `qhhxx7a2fcbzk2p2bj257c7uhrjorzhnyefuo34epmm3vlooqwemfmad.onion`

Since Tor does not support UDP, the DNS query must be sent via TCP. This is done using
the Tor Socks5 proxy, which is reachable via `localhost:9050` by default. Note that
depending on distribution, the proxy might or might not be enabled by default when using
Tor (for NixOS, simply set `darkseed.client.enable` = true).

Example:

```bash
 darkdig dnsseed.21.ninja. --type ANY --nameserver qhhxx7a2fcbzk2p2bj257c7uhrjorzhnyefuo34epmm3vlooqwemfmad.onion --socks5-proxy 127.0.0.1:9050 --tcp
; <<>> darkdig 0.10.0 <<>> @qhhxx7a2fcbzk2p2bj257c7uhrjorzhnyefuo34epmm3vlooqwemfmad.onion -p 53 --socks5-proxy 127.0.0.1:9050 --tcp dnsseed.21.ninja.
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 41195
;; flags: qr rd, QUERY: 1, ANSWER: 3, AUTHORITY: 0, ADDITIONAL: 0

;;QUESTION SECTION:
; domain=dnsseed.21.ninja., rdclass=IN, rdtype=ANY

;;ANSWER SECTION:
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=100.20.110.240
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=167.99.6.85
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=50.83.111.96
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=198.7.114.58
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=109.199.103.39
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=95.217.77.101
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=203.11.72.6
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=47.62.225.47
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=213.168.187.27
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=34.106.58.234
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2001:fb1:ba:9c18:3b4c:ee66:2d1:684f
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2605:6440:3001:2f:3eec:efff:fe91:f840
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a03:b0c0:3:d0::f3e:3001
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a01:7e01::f03c:94ff:fe79:2d9c
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fccb:248:11a6:1042:bca:1218:f7ce:7d3d
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fcf1:22ff:3070:582f:a873:61bc:4bc1:81bf
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=NULL
;; ->>custom NULL encoding<<- size: 133, records: 4, data (base64): BACAO7R4TrNHBXVG3lymrTI932H+6PX8yftgNy14zHnkAwA3Kli7EereSNmQiSvmihaQNR/2XSzPyi/5Fxau0VXs6wEfFuuraV29ZBBvp4XnishsKyu3/pVDvervN9WDljIbzwEgTzkjMQS6GrY33vSQNgTM+YSyRx5H9zUM8DvsZll2pA
;; ->>custom NULL-encoded address <<- record: 0, address: qa53i6cowndqk5kg3zoknljshxpwd7xi6x6mt63ag4wxrtdz4qbyhhid.onion
;; ->>custom NULL-encoded address <<- record: 1, address: g4vfroyr5lperwmqrev6ncqwsa2r75s5fth4ul7zc4lk5ukv5tvrddyd.onion
;; ->>custom NULL-encoded address <<- record: 2, address: d4loxk3jlw6wiedpu6c6pcwinqvsxn76svb332xpg7kyhfrsdphq.b32.i2p
;; ->>custom NULL-encoded address <<- record: 3, address: ebhtsizras5bvnrx332janqezt4yjmshdzd7onim6a56yzszo2sa.b32.i2p

;; Query time: 4546 msec
;; SERVER: qhhxx7a2fcbzk2p2bj257c7uhrjorzhnyefuo34epmm3vlooqwemfmad.onion#53
;; WHEN: Wed Sep 04 16:01:24 CEST 2024
;; MSG SIZE  rcvd: 507
```

### I2P

Instances are reachable under the following addresses:
- `ja7o42qnralhke5kwsatycm7hj4ssq6gqwdrcsjvgt3xe3a2tvga.b32.i2p`
- `4ibvyflekkqc45domfbdlfp7zudurmd7x6whd4x5q7vsor7sgwtq.b32.i2p`

Since I2P does not support UDP, the DNS query must be sent via TCP. This is done using
the Onion Socks5 proxy, which is reachable via `localhost:4447` by default. Note that
depending on distribution, the proxy might or might not be enabled by default when using
I2P (for NixOS, simply set `darkseed.client.enable` = true).

Example:

```bash
 darkdig dnsseed.21.ninja. --type ANY --nameserver ja7o42qnralhke5kwsatycm7hj4ssq6gqwdrcsjvgt3xe3a2tvga.b32.i2p --socks5-proxy 127.0.0.1:4447 --tcp
; <<>> darkdig 0.10.0 <<>> @ja7o42qnralhke5kwsatycm7hj4ssq6gqwdrcsjvgt3xe3a2tvga.b32.i2p -p 53 --socks5-proxy 127.0.0.1:4447 --tcp dnsseed.21.ninja.
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 22197
;; flags: qr rd, QUERY: 1, ANSWER: 3, AUTHORITY: 0, ADDITIONAL: 0

;;QUESTION SECTION:
; domain=dnsseed.21.ninja., rdclass=IN, rdtype=ANY

;;ANSWER SECTION:
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=3.68.109.55
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=161.35.54.110
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=85.195.244.202
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=198.144.183.184
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=136.243.104.27
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=75.36.7.189
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=37.34.182.236
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=173.249.7.254
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=174.0.23.151
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=183.88.244.125
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2407:8800:bc61:2220:555b:7e78:78a0:eb32
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2001:41d0:248:ac00::2
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a01:4f9:4a:1385::2
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2602:47:2475:1600::1
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fca0:151:79ac:8992:b51e:bdc4:6ed9:41be
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc32:17ea:e415:c3bf:9808:149d:b5a2:c9aa
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=NULL
;; ->>custom NULL encoding<<- size: 133, records: 4, data (base64): BABJlYrnCBTnk5U2erb2FIqaB0NXRpHqhyPp25GD1JBTLABSYidMcyLDT+P38pigOeouSxmfluOVkUS7GCN3qdkIOAHiT8t9BakqD0T/XppGQdHgAgU70HfiNMNeXHwGld4wZAEBh7IGPJsUnr2xoqVj/XS6vhLMa2mtWrZ5aLUY9BZQIQ
;; ->>custom NULL-encoded address <<- record: 0, address: jgkyvzyicttzhfjwpk3pmfektidugv2gshvioi7j3oiyhveqkmwmhhid.onion
;; ->>custom NULL-encoded address <<- record: 1, address: kjrcotdtelbu7y7x6kmkaopkfzfrth4w4okzcrf3darxpkozba4oj4yd.onion
;; ->>custom NULL-encoded address <<- record: 2, address: 4jh4w7ifveva6rh7l2nemqor4abako6qo7rdjq26lr6anfo6gbsa.b32.i2p
;; ->>custom NULL-encoded address <<- record: 3, address: agd3ebr4tmkj5pnrukswh7luxk7bftdlngwvvntznc2rr5awkaqq.b32.i2p

;; Query time: 2287 msec
;; SERVER: ja7o42qnralhke5kwsatycm7hj4ssq6gqwdrcsjvgt3xe3a2tvga.b32.i2p#53
;; WHEN: Wed Sep 04 16:03:22 CEST 2024
;; MSG SIZE  rcvd: 507
```

### Cjdns

Instances are reachable under the following addresses:
- `fc1f:3640:c8e1:af7:d177:f6c9:e443:6fdf`
- `fcf9:45bc:8c48:6973:7b3f:5538:6e51:8fc9`

Cjdns works transparently and supports UDP, so no proxy and DNS over TCP is required.

Example:

```bash
darkdig dnsseed.21.ninja. --type ANY --nameserver fc1f:3640:c8e1:af7:d177:f6c9:e443:6fdf
; <<>> darkdig 0.10.0 <<>> @fc1f:3640:c8e1:af7:d177:f6c9:e443:6fdf -p 53 dnsseed.21.ninja.
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 33234
;; flags: qr rd, QUERY: 1, ANSWER: 3, AUTHORITY: 0, ADDITIONAL: 0

;;QUESTION SECTION:
; domain=dnsseed.21.ninja., rdclass=IN, rdtype=ANY

;;ANSWER SECTION:
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=77.38.3.90
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=108.48.39.246
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=45.135.232.99
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=109.146.128.196
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=118.172.148.236
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=34.204.100.116
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=82.64.162.213
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=51.77.119.85
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=84.146.196.78
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=103.78.113.152
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2600:1700:5453:69e::109
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a00:11c0:60:294:c48f:beff:fe15:a97f
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2001:1620:5566:100::62c
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2001:19f0:5001:389b:5400:4ff:fe8a:5bc6
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc6d:f562:86a0:791d:8a20:7aa2:8879:2176
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc32:2c16:d0d0:f1fb:3b27:c187:8cb5:9201
domain=dnsseed.21.ninja., ttl=60, rdclass=IN, rdtype=NULL
;; ->>custom NULL encoding<<- size: 133, records: 4, data (base64): BAAD0KfgcbnOFxutK4v2RpKg8PxpVuts63pYgz3aoDZrEQAEaBJ7Vnt0Ne1YK1m8QnlkESvaiU6Js40C40GSRd4vlgHkzsqsBmTGDzC5VorSAqkXtz3wW9dq4povDuAF4F7TpQHVbPKvwq/R2YKwba1RdT12fSrLT/6L2CThkHUqMqE8dQ
;; ->>custom NULL-encoded address <<- record: 0, address: apikpydrxhhbog5nfof7mrusudypy2kw5nwow6syqm65vibwnmi7ouyd.onion
;; ->>custom NULL-encoded address <<- record: 1, address: arube62wpn2dl3kyfnm3yqtzmqisxwujj2e3hdic4nazero6f6lkr7id.onion
;; ->>custom NULL-encoded address <<- record: 2, address: 4thmvlagmtda6mfzk2fneavjc63t34c325vofgrpb3qalyc62osq.b32.i2p
;; ->>custom NULL-encoded address <<- record: 3, address: 2vwpfl6cv7i5tavqnwwvc5j5oz6svs2p72f5qjhbsb2sumvbhr2q.b32.i2p

;; Query time: 21 msec
;; SERVER: fc1f:3640:c8e1:af7:d177:f6c9:e443:6fdf#53
;; WHEN: Wed Sep 04 16:06:17 CEST 2024
;; MSG SIZE  rcvd: 507
```

## Hints

To test the Darknet availability of one's own `darkseed` instance, the following might
be helpful.

On NixOS, a `darkseed` instance's
- Onion address can be found in the file `/var/lib/tor/onion/darkseed/hostname`
- I2P address can be derived by appending `.b32.i2p` to the result of `sudo head -c 391
  /var/lib/i2pd/darkseed-keys.dat | sha256sum | cut -f1 -d\  | xxd -r -p | base32 | tr
  '[:upper:]' '[:lower:]' | sed -r 's/=//g'`
- Cjdns address is associated with the `tun0` interface (`ip -6 addr show dev tun0 | awk
  '/inet6/ && /global/ {print $2; exit}' | cut -d'/' -f1`)
