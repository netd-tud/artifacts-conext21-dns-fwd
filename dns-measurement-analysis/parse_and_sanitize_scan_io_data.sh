#!/bin/bash

workdir="$(pwd)"
export workdir
#readin arguments
pcap_dir=$1
export pcap_dir

csv_dir=$2
export csv_dir


tasks="${workdir}/.tasks.txt"

dns_sanitize="ip and not icmp and udp and dns"
export dns_sanitize

parse_and_sanitize(){
    pcapfile=$1
    csvfile=$(basename ${pcapfile} | cut -d. -f1)
    csvfile="${csvfile}.csv"
    
    tshark -nr $pcapfile -Y "$dns_sanitize" \
	-e frame.number -e frame.time_epoch -e ip.src -e ip.ttl -e ip.dst -e dns.id \
	-e udp.srcport -e udp.dstport -e dns.flags.response \
	-e dns.qry.type -e dns.flags.opcode -e dns.flags.authoritative \
        -e dns.flags.truncated -e dns.flags.recdesired -e dns.flags.recavail \
        -e dns.flags.rcode -e dns.count.queries -e dns.count.answers \
        -e dns.count.auth_rr -e dns.count.add_rr -e dns.qry.name -e dns.resp.name -e dns.resp.ttl -e dns.a \
	-E header=y -E separator=\; -E occurrence=a -E quote=d -E aggregator=, \
	-T fields -o ip.defragment:FALSE | gzip > $csv_dir/$csvfile.gz
    
    #parallel -j 1 --progress python3 $workdir/parse_and_sanitize.py $pcap_dir/$csvfile $workdir/sanitized-data/
    
}

export -f parse_and_sanitize
echo $pcap_dir

#get all pcap filenames and store in a task file
find "$pcap_dir" -name '*.pcap.gz' | sort > "${tasks}"
parallel --bar -j 12 -k parse_and_sanitize < "${tasks}"
