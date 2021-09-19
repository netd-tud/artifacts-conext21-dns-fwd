#!/bin/bash

# get current vp mode
mode=$(cat config_vp.txt)

# drop all ICMP traffic by the OS because it reports used ports still as closed
# scapy works by sniffing the traffic and forging packets via raw sockets
if [ "$mode" = "ixp" ]; then
    iptables -A INPUT -d 91.216.216.0/24 -p icmp -j DROP
    iptables -A OUTPUT -s 91.216.216.0/24 -p icmp -j DROP
fi

# we set iptables rules, then clean up (remove duplicate firewall entries)
# https://serverfault.com/a/890065
# https://iridakos.com/programming/2019/05/16/remove-duplicate-lines-preserving-order-linux
iptables-save | awk '!seen[$0]++' | iptables-restore
echo "All ICMP traffic to current /24 will be dropped now."

iptables-save
