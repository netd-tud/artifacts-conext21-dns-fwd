# DNS Honeypot Sensors

These scripts emulate 3 different types of open DNS speakers. The supported _modes_ are as follows:

1. `proxy`: Recursive resolver. Incoming requests are resolved via a public resolver (e.g., Google). The answer is then relayed as-is to the querist. IP address of the response is the IP address of the sensor. This mode behaves like the common DNS amplifier.
2. `localfwd`: Multi-interface resolver. Incoming requests are resolved via a public resolver (e.g., Google). IP address of the response is *not* the IP address of the sensor but actually another IP address from the same prefix.
3. `remotefwd`: Transparent forwarder. Incoming requests are *forwarded* to a a public resolver (e.g., Google). This means we spoof the source IP address of the querist and that this sensor never observes the response -- the public resolver responds directly to the querist.

## Requirements

### Python Tools

This implementation is written in Python3. The only non-default requirements are:

```python
scapy
cachetools
```

### Firewall

This implementation uses raw sockets which do not bind on specific ports. This means that next to our DNS response the OS will also automatically send an `ICMP not reachable` message for each incoming request. We have to suppress this. We do this prefix-wide with iptables, compare `./block_icmp.sh`.

You can adjust the network prefix in this script for each vantage point type. Existing rules will remains untouched, we only append an `ICMP DROP` rule. Please see the configuration section.

### Network Infrastructure

If you want these sensors to work globally, i.e. any DNS scanner is able to discover these sensors, you need a publicly routed prefix; we use `91.216.216.0/24` which is announced at an IXP. Also, you need an Upstream which does not filter spoofed packets or a direct link to the public DNS resolver (e.g., Google).

## Configuration

### Vantage Point Name

First, you need to define a vantage point name in `config_vp.txt`, we use `ixp`:

```bash
$ cat config_vp.txt
ixp
```

### Vantage Point Firewall

You need to add a firewall configuration for this vantage point and its prefix in `block_icmp.sh`:

```bash
if [ "$mode" = "ixp" ]; then
    iptables -A INPUT -d 91.216.216.0/24 -p icmp -j DROP
    iptables -A OUTPUT -s 91.216.216.0/24 -p icmp -j DROP
fi
```

### Vantage Point Sensors

Then, you can add your vantage point, prefix, and interfaces to `forwarder.py`:

Add current /24 prefix for vantage point:

```python
prefixes = {
        "ixp": "91.216.216"
    }
prefix = prefixes[vp]
```

Configure interfaces:

`in` interface is used for receiving requests from clients. In our case, we can receive traffic for the current prefix on 3 different interfaces.

`dns` interface is used for communicating with the public DNS resolver.

`out` interface is used for sending final DNS packet, i.e. final reply to clients or spoofed packet to resolver in  `remotefwd` mode.

```python
ifaces = {
        ("proxy","ixp","in"):       (["eno3","vlan100","vlan224"],f"{prefix}.51"),
        ("proxy","ixp","dns"):      ("vlan100",f"193.178.185.26"),
        ("proxy","ixp","out"):      ("eno3",f"{prefix}.51"),

        ("localfwd","ixp","in"):    (["eno3","vlan100","vlan224"],f"{prefix}.52"),
        ("localfwd","ixp","dns"):   ("vlan100",f"193.178.185.26"),
        ("localfwd","ixp","out"):   ("eno3",f"{prefix}.53"),

        ("remotefwd","ixp","in"):   (["eno3","vlan100","vlan224"],f"{prefix}.54"),
        ("remotefwd","ixp","dns"):  (None,None),
        ("remotefwd","ixp","out"):  ("eno3",None),
    }
```

You can also configure the public resolver:

```python
RESOLVER_LIST = {
        "Q1": "1.1.1.1",
        "Q8": "8.8.8.8",
        "Q9": "9.9.9.9",
    }
RESOLVER_IP = RESOLVER_LIST["Q8"]
```

## Compilation & Running

Per default, the sensors listen on port 53. You need root rights to run the sensors.

```bash
sudo ./block_icmp.sh
sudo ./run.sh proxy      # in: prefix.51, out: prefix.51
sudo ./run.sh localfwd   # in: prefix.52, out: prefix.53
sudo ./run.sh remotefwd  # in: prefix.54, out: xxx
```

## Testing

Running these sensors locally should work as described above. However, the sensors require a very specific environment to operate globally. Therefore, to offer a real-world test, we currently run our servers which you can test against. 

Warning: These tests will not work if your scanning behind a NAT. This is because you will receive answers from IP addresses for which you did not initiate a communication. This applies to `localfwd` and `remotefwd` mode.

Also, please keep in mind that the honeypots are configured with a rate limiting. You will receive only one answer per 5 minutes from each sensor:

```python
# rate limit per /24 prefix
p24_ttl = 10 if debug else 300
p24_cache = TTLCache(maxsize=100000, ttl=p24_ttl)
```

To test our servers, simply run:

```bash
./test.sh  # test requires dig and no NAT, works every 5 minutes per src /24
```

### Expected Output

```bash
===== Test 1: proxy @91.216.216.51 =====
;; ANSWER SECTION:
google.com.		106	IN	A	216.58.213.238
--
;; SERVER: 91.216.216.51#53(91.216.216.51)
;; WHEN: Sun Sep 19 16:13:39 CEST 2021

===== Test 2: localfwd @91.216.216.52 =====
;; ANSWER SECTION:
google.com.		106	IN	A	216.58.213.238
--
;; SERVER: 91.216.216.53#53(91.216.216.52)
;; WHEN: Sun Sep 19 16:13:40 CEST 2021

===== Test 3: remotefwd @91.216.216.54 =====
;; ANSWER SECTION:
google.com.		106	IN	A	216.58.213.238
--
;; SERVER: 8.8.8.8#53(91.216.216.54)
;; WHEN: Sun Sep 19 16:13:41 CEST 2021
```
