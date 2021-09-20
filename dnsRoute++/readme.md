# DNSRoute++

This toolchain checks whether a given host (identified by an IP address) behaves like a transparent forwarder. Then, it maps the complete path until the host (similar to regular traceroute) and beyond, i.e., the path between the transparent forwarder and its recursive resolver.

## Requirements

### Python Tools

This implementation is written in Python3. The non-default requirements are:

```python
scapy
matplotlib
pandas
numpy
```

### Network Infrastructure

This script sends bursts (default=30) of DNS requests for the same name. Some DDoS mitigation might be sensible to this. Also, for transparent forwarders, you will receive DNS responses  from hosts which you did not contact in the first place. This means that your scanner must not be behind a NAT middlebox.

## Configuration

### Burst Size

We are sending DNS request burst to map the paths. The default is to send 30 packets, each with an increasing TTL (0..29). In some rare cases you might want to increase the burst size:

```python
MAX_TTL = 30
```

### Interface Settings

Adjust source interface and IP address directly in the script:

```python
IP_CLIENT = "141.22.28.227"
IFACE_CLIENT = "eno1"
```

## Compilation & Running

Install all dependencies. Then, simply execute the run command below with root rights.

### Single IP address

To test whether a single IP address is a transparent forwarder, please run:

```bash
sudo ./isTranspFwd.sh $ip  # requires dig
```

To perform dnsRoute++ measurement for a single IP address, please run:

```bash
sudo ./run.py $ip  # configure (interface,ip) in dnsRoute script
```

## Testing

Testing dnsRoute++ without real transparent forwarders does not show its unique features. Therefore, we include a hitlist of candidate IP addresses in `ip_list.txt.gz` . These are very likely to be transparent forwarders. Executing `run.sh` without an argument will traverse all IP addresses in the hitlist. You can interrupt the scan anytime.

### Large Scale Measurements

```bash
sudo ./run.sh  # no argument triggers hitlist mode, configure (interface,ip) in dnsRoute script
```

### Expected Output

For each transparent forwarder, you will find a file in `logs/` . We include 3 sample files as a reference. The log files are compressed CSV files with the following schema:

```bash
hop.id|ip.response|ts.utc|ip.scanner|ip.target|pkt.layers
```

Example below for `103.97.77.129`: Please note that we reach the transparent forwarder at hop 15 and continue to map the path until its public resolver `8.8.8.8` at hop 23.

```bash
$ zcat sample_dnsroute_103.97.77.129.csv.gz
0|141.22.28.1|2021-07-29 18:08:03.057401|141.22.28.227|103.97.77.129|Ether / IP / ICMP 141.22.28.1 > 141.22.28.227 time-exceeded ttl-zero-during-transit / IPerror / UDPerror
1|141.22.28.1|2021-07-29 18:08:03.058744|141.22.28.227|103.97.77.129|Ether / IP / ICMP 141.22.28.1 > 141.22.28.227 time-exceeded ttl-zero-during-transit / IPerror / UDPerror
2|141.22.4.148|2021-07-29 18:08:03.060273|141.22.28.227|103.97.77.129|Ether / IP / ICMP 141.22.4.148 > 141.22.28.227 time-exceeded ttl-zero-during-transit / IPerror / UDPerror
3|188.1.237.173|2021-07-29 18:08:03.074027|141.22.28.227|103.97.77.129|"Ether / IP / ICMP / IPerror / UDPerror / DNS Qry ""b'rr-mirror.research.nawrocki.'"" "
4|193.178.185.34|2021-07-29 18:08:03.074716|141.22.28.227|103.97.77.129|"Ether / IP / ICMP / IPerror / UDPerror / DNS Qry ""b'rr-mirror.research.nawrocki.berlin.'"" "
5|184.105.223.110|2021-07-29 18:08:03.090222|141.22.28.227|103.97.77.129|"Ether / IP / ICMP / IPerror / UDPerror / DNS Qry ""b'rr-mirror.research.nawrocki.berlin.'"" "
6|184.105.65.41|2021-07-29 18:08:03.100262|141.22.28.227|103.97.77.129|Ether / IP / ICMP 184.105.65.41 > 141.22.28.227 time-exceeded ttl-zero-during-transit / IPerror / UDPerror
7|72.52.92.130|2021-07-29 18:08:03.101770|141.22.28.227|103.97.77.129|"Ether / IP / ICMP / IPerror / UDPerror / DNS Qry ""b'rr-mirror.research.nawrocki.berlin.'"" "
8|184.104.195.178|2021-07-29 18:08:03.107009|141.22.28.227|103.97.77.129|"Ether / IP / ICMP / IPerror / UDPerror / DNS Qry ""b'rr-mirror.research.nawrocki.berlin.'"" "
9|184.104.193.125|2021-07-29 18:08:03.189217|141.22.28.227|103.97.77.129|Ether / IP / ICMP 184.104.193.125 > 141.22.28.227 time-exceeded ttl-zero-during-transit / IPerror / UDPerror
10|184.105.65.13|2021-07-29 18:08:03.247121|141.22.28.227|103.97.77.129|Ether / IP / ICMP 184.105.65.13 > 141.22.28.227 time-exceeded ttl-zero-during-transit / IPerror / UDPerror
11|65.49.108.46|2021-07-29 18:08:03.249621|141.22.28.227|103.97.77.129|"Ether / IP / ICMP / IPerror / UDPerror / DNS Qry ""b'rr-mirror.research.nawrocki.'"" "
14|103.129.248.19|2021-07-29 18:08:03.268866|141.22.28.227|103.97.77.129|"Ether / IP / ICMP / IPerror / UDPerror / DNS Qry ""b'rr-mirror.research.nawrocki.berlin.'"" "
15|103.97.77.129|2021-07-29 18:08:03.270506|141.22.28.227|103.97.77.129|"Ether / IP / ICMP / IPerror / UDPerror / DNS Qry ""b'rr-mirror.research.nawrocki.berlin.'"" "
16|103.129.248.19|2021-07-29 18:08:03.271780|141.22.28.227|103.97.77.129|"Ether / IP / ICMP / IPerror / UDPerror / DNS Qry ""b'rr-mirror.research.nawrocki.berlin.'"" "
17|103.129.248.18|2021-07-29 18:08:03.272724|141.22.28.227|103.97.77.129|Ether / IP / ICMP 103.129.248.18 > 141.22.28.227 time-exceeded ttl-zero-during-transit / IPerror / UDPerror
20|74.125.118.220|2021-07-29 18:08:03.351729|141.22.28.227|103.97.77.129|"Ether / IP / ICMP / IPerror / UDPerror / DNS Qry ""b'rr-mirror.research.nawrocki.'"" "
21|209.85.255.81|2021-07-29 18:08:03.357193|141.22.28.227|103.97.77.129|"Ether / IP / ICMP / IPerror / UDPerror / DNS Qry ""b'rr-mirror.research.nawrocki.'"" "
22|72.14.232.107|2021-07-29 18:08:03.355483|141.22.28.227|103.97.77.129|"Ether / IP / ICMP / IPerror / UDPerror / DNS Qry ""b'rr-mirror.research.nawrocki.'"" "
23|8.8.8.8|2021-07-29 18:08:03.794656|141.22.28.227|103.97.77.129|"Ether / IP / UDP / DNS Ans ""172.217.44.202"" "
24|8.8.8.8|2021-07-29 18:08:03.798946|141.22.28.227|103.97.77.129|"Ether / IP / UDP / DNS Ans ""172.217.47.1"" "
25|8.8.8.8|2021-07-29 18:08:03.796348|141.22.28.227|103.97.77.129|"Ether / IP / UDP / DNS Ans ""74.125.190.133"" "
26|8.8.8.8|2021-07-29 18:08:03.722094|141.22.28.227|103.97.77.129|"Ether / IP / UDP / DNS Ans ""74.125.190.148"" "
27|8.8.8.8|2021-07-29 18:08:03.844012|141.22.28.227|103.97.77.129|"Ether / IP / UDP / DNS Ans ""172.217.43.137"" "
28|8.8.8.8|2021-07-29 18:08:03.785123|141.22.28.227|103.97.77.129|"Ether / IP / UDP / DNS Ans ""172.217.44.194"" "
29|8.8.8.8|2021-07-29 18:08:03.754496|141.22.28.227|103.97.77.129|"Ether / IP / UDP / DNS Ans ""172.253.211.67"" "
```
