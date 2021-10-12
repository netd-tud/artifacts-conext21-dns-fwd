#!/bin/bash

# config:
#  rotate every 100MB, only record dns responses (and not ICMP backscatter)

source config_file
pcap_max_size="100000"

mode=$1
dir_pcaps="./pcaps_dns_$mode/dns_complete_scan"
mkdir -p $dir_pcaps
name_pcaps="${dir_pcaps}/dns_${mode}_$(date +%s).pcap"
#scan_filter="dst ${node_ip} and not icmp and udp src port 53"
#capture also outgoing packets
scan_filter="not icmp and udp port 53"

# capture filter is only the first sanity check
dumpcap -Pi "$interface" \
    -f "$scan_filter" \
    -w "$name_pcaps" \
    -b filesize:"$pcap_max_size"

# fix access rights
chmod -R 775 "${dir_pcaps}"
