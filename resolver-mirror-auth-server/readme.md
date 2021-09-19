# RR-Mirror Nameserver

This is a DNS nameserver which responds with dynamically created DNS answers, based on IP address of the querist. This server can be used to differentiate between recursive resolvers and forwarders.

Each DNS answer includes two A records:

1. Source IP address of the DNS query
2. Control IP address (always `91.216.216.216`)

## Requirements

### GO Tools

This implementation is written in GO. Get the build tools with e.g.:

````bash
sudo pacman -S go
````

The only non-default requirement is Miekg's DNS library:

```bash
go get github.com/miekg/dns
go build github.com/miekg/dns
```

### DNS Infrastructure

If you want this server to work globally, i.e. any DNS client is able to receive a mirrored response from this nameserver, you need zone under your control in the DNS.

We own the zone `.nawrocki.berlin.` and refer all queries for `*.research.nawrocki.berlin.` to the rr-mirror. We did this by creating an `A` record for the rr-mirror named `ns.nawrocki.berlin.` and then setting the `NS` record pointing to it.

## Configuration

You can set the server's public IP address and port in `rr-mirror.go`:

```go
server_ip := "141.22.213.44"
server_port := 53
```

The name(s) for which the server should create mirrored answers is also configurable:

```go
var records = map[string]bool{
    rr-mirror.research.nawrocki.berlin.": true,
}
```

The control record can be changed (other IP address, TTL, etc.) in the second `A` struct:

```go
rr_a_static := &dns.A {
            Hdr: dns.RR_Header {
                Name: q.Name,
                Rrtype: dns.TypeA,
                Class: dns.ClassINET,
                Ttl: 3600 },
            A: net.ParseIP("91.216.216.216")
```

## Compilation & Running

Compile with GO-tools:

```bash
go build ./rr-mirror.go`
```

Per default, the server listens on port 53. You need root rights to run the server.

```bash
sudo ./rr-mirror
```

## Testing

Building this server with GO tools and running it locally should work as described above. However, clients will not be able to reach this server via a normal name resolution.

Therefore, to offer a real-world test, we run a rr-mirror server which you can test against. Simpy run:

```bash
./test.sh  # test requires dig
```

### Expected Output

```bash
===== Test 1: Remote Resolver Default =====
$IP_DEFAULT_RESOLVER
91.216.216.216
===== Test 2: Remote Resolver Quad9 =====
$IP_QUAD9_BACKEND_RESOLVER
91.216.216.216
===== Test 3: Local Resolver =====
$IP_YOUR_PUBLIC_ADDRESS
91.216.216.216
```
