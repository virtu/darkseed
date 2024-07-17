# darkseed

A DNS seeder for Bitcoin supporting all network types.

## Components

### darkdig

Tool to query a DNS peer and decode custom DNS NULL records used by `darkseed`.

Example:

```bash
darkdig seed.21.ninja --nameserver 127.0.0.1 -p 8053 -v
; <<>> darkdig 0.1.0 <<>> @127.0.0.1 -p 8053 -v seed.21.ninja
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 64611
;; flags: qr rd, QUERY: 1, ANSWER: 3, AUTHORITY: 0, ADDITIONAL: 0

;;QUESTION SECTION:
; domain=seed.21.ninja., rdclass=IN, rdtype=A

;;ANSWER SECTION:
; domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=NULL
; ->>custom NULL encoding<<- size: 133, records: 4, data (base64): BADlX6fJH9wLJ4vNI4b7uuThyXecuYdWt0ogP0yuNTY7fgC2UPMovBhvC+qhE5vX8qV2jXsMGNatZGWQW/cCe0beVgGhrdyE8tPrI10EUtgvZ5nw+iril+PFN5dUGdJr1Al09AFXvroRHeKFpJJEU5ym1eZhDoOcribiHiVksmjY3GaR/w
; ->>custom NULL encoding<<- record: 0, address: 4vp2psi73qfspc6neodpxoxe4hexphfzq5llosrah5gk4njwhn7hzlqd.onion
; ->>custom NULL encoding<<- record: 1, address: wzipgkf4dbxqx2vbcon5p4vfo2gxwday22wwizmqlp3qe62g3zliatad.onion
; ->>custom NULL encoding<<- record: 2, address: ugw5zbhs2pvsgxieklmc6z4z6d5cvyux4pctpf2udhjgxvajot2a.b32.i2p
; ->>custom NULL encoding<<- record: 3, address: k67luei54kc2jesekooknvpgmehihhfoe3rb4jlewjunrxdgsh7q.b32.i2p
; domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fccb:248:11a6:1042:bca:1218:f7ce:7d3d
; domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=fc6d:f562:86a0:791d:8a20:7aa2:8879:2176
; domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2001:b011:e002:df83:3cdd:7949:320d:865b
; domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a04:52c0:104:160c::1
; domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a05:d012:42a:5701:cbeb:c40e:a5eb:318d
; domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=AAAA, data=2a01:4f9:2b:2655::2
; domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=188.60.101.105
; domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=203.59.154.173
; domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=1.234.244.89
; domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=69.4.94.226
; domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=87.122.8.70
; domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=222.186.20.60
; domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=192.99.0.26
; domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=78.8.77.58
; domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=54.193.21.65
; domain=seed.21.ninja., ttl=60, rdclass=IN, rdtype=A, data=165.227.203.131
```

NOTE: The repository contains a Nix flake so to test without installing you can use `nix
shell . -c darkdig seed.21.ninja --nameserver 127.0.0.1 -p 8053`.
