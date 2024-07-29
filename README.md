# darkseed

A DNS seeder for Bitcoin supporting all network types.

## Components

### darkdig

Tool to query a DNS peer and decode custom DNS NULL records used by `darkseed`.

Example:

```bash
darkdig seed.21.ninja. --nameserver 65.21.252.171
; <<>> darkdig 0.1.0 <<>> @65.21.252.171 -p 53 seed.21.ninja.
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 20782
;; flags: qr rd, QUERY: 1, ANSWER: 3, AUTHORITY: 0, ADDITIONAL: 0

;;QUESTION SECTION:
; domain=seed.21.ninja., rdclass=IN, rdtype=A

;;ANSWER SECTION:
domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=NULL
;; ->>custom NULL encoding<<- size: 133, records: 4, data (base64): BADgSkKoWXhu1bfnzGpGNkkEIzSTOAgAoZ5/J2wtc1IAngBp4Dtx743NW94Xmgeyxv2f9zExg1dkC/wc2LtR+bC3iwFJfOkRvTRPeJfKkPxUV6Vw/miozV++IkwoJFU/9njzYgHHxAOAW7YP5V6BshWIuCTngs6c5OOrdvCX9kunJUoFow
;; ->>custom NULL-encoded address <<- record: 0, address: 4bfefkczpbxnln7hzrvemnsjaqrtjezybaakdht7e5wc242sacpizhid.onion
;; ->>custom NULL-encoded address <<- record: 1, address: nhqdw4pprxgvxxqxtid3frx5t73tcmmdk5sax7a43c5vd6nqw6fxpxad.onion
;; ->>custom NULL-encoded address <<- record: 2, address: jf6osen5grhxrf6ksd6fiv5fod7grkgnl67cetbierkt75ty6nra.b32.i2p
;; ->>custom NULL-encoded address <<- record: 3, address: y7cahac3wyh6kxubwikyrobe46bm5hhe4ovxn4ex6zf2ojkkawrq.b32.i2p
domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fca0:151:79ac:8992:b51e:bdc4:6ed9:41be
domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc32:17ea:e415:c3bf:9808:149d:b5a2:c9aa
domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a02:c206:2181:1209::1
domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2003:e3:f746:aa00:be24:11ff:fe64:c6a
domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2406:da18:9f1:f300:6d30:bf12:8a1b:873b
domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a01:4f9:1a:ae1a::2
domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=3.144.223.134
domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=16.163.188.199
domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=3.132.226.114
domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=15.207.111.189
domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=191.255.221.37
domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=84.56.144.51
domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=70.76.245.12
domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=149.202.85.112
domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=78.46.80.246
domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=185.210.125.33

;; Query time: 77 msec
;; SERVER: 65.21.252.171#53
;; WHEN: Thu Jul 18 11:13:12 CEST 2024
;; MSG SIZE  rcvd: 504
```

NOTE: The repository contains a Nix flake so to test without installing you can use `nix
shell . -c darkdig seed.21.ninja --nameserver 127.0.0.1 -p 8053`.

## Local Testing (with Nix)

Make sure to make reachable node data (generated with `p2p-crawler`) available in a
`node_data` directory under the git repository root.

```bash
# Start a darkseed instance serving nodes via DNS on port 8053 and via REST on port 8080
nix run . -- --log-level debug --crawler-path $(git rev-parse --show-toplevel)/test_data --dns-port 8053 --rest-port 8080

# Testing the DNS interface
nix shell . -c darkdig seed.21.ninja. --nameserver 127.0.0.1 -p 8053

# Testing the REST interface
curl 127.0.0.1:8080/nodes/ipv4
```

## Darknet availability (Tor, I2P and Cjdns)

The REST interface of a demo `darkseed` instance is reachable via Tor, I2P, and Cjdns.

### Tor

Address `qhhxx7a2fcbzk2p2bj257c7uhrjorzhnyefuo34epmm3vlooqwemfmad.onion` on port 48180.

Assuming a working Onion tor socks5 proxy (running on `localhost:9050` by default), the
instance can be queried as follows:

```bash
curl --socks5-hostname localhost:9050 http://qhhxx7a2fcbzk2p2bj257c7uhrjorzhnyefuo34epmm3vlooqwemfmad.onion:48180/nodes

[{"address":"3cd6wc557gesvdcvr35bb45ofks44beh6hhy2lai5bcqrud2duy6ysad.onion"},{"address":"3.130.132.234"},...]
```

### I2P

Address `m2g2kz53anuokcdzkmiak7kzpxt5ropmftffseeqiu3zjvax6cua.b32.i2p` on port 48180.

Assuming a working I2P HTTP proxy (running on `localhost:4444`, if enabled, e.g., via
setting `services.i2pd.proto.httpProxy.enable` to true on NixOS), the instance can be
queried as follows:

```bash
curl --proxy http://localhost:4444 http://m2g2kz53anuokcdzkmiak7kzpxt5ropmftffseeqiu3zjvax6cua.b32.i2p/nodes

[{"address":"sirb7csejtk7xwr6qymggudtft6cwd5d4iroj4vlajhiipt2hiaq.b32.i2p"},{"address":"h4bxizfku3lgjbemw5orbuluugq5uv2nglrtj2vusy2gxdhwj5u6mtad.onion"},...]
```

### Cjdns

Address `fcf9:45bc:8c48:6973:7b3f:5538:6e51:8fc9` on port 48180.

The instance can be queried as follows:

```bash
curl http://[fcf9:45bc:8c48:6973:7b3f:5538:6e51:8fc9]:48180/nodes

[{"address":"198.154.99.66"},{"address":"185.66.143.190"},{"address":"bg76hlijkwluqqgpiahkdijpffdim6ed6tgwuovoysv2vnnhrahtkdyd.onion"},...]
```

### Misc

To test the darknet availability of one's own `darkseed` instance, the following might
be helpful.

On NixOS, an instances
- Onion address can be found in the file `/var/lib/tor/onion/darkseed/hostname`.
- I2P address can be derived by appending `.b32.i2p` to the result of `sudo head -c 391
  /var/lib/i2pd/darkseed-keys.dat | sha256sum | cut -f1 -d\  | xxd -r -p | base32 | tr
  '[:upper:]' '[:lower:]' | sed -r 's/=//g'`
- Cjdns address is associated with the `tun0` interface (`ip -6 addr show dev tun0 | awk
  '/inet6/ && /global/ {print $2; exit}' | cut -d'/' -f1`)
