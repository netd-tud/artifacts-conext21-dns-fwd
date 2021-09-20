#! /usr/bin/env python3
###############################################################################

# just here to remove stupid warning about missing x-server / display
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from scapy.all import Ether, IP, ICMP, UDP, UDPerror, DNS, DNSQR
from scapy.all import conf, RandShort, sniff

import sys
import random
from time import sleep
from datetime import datetime
from multiprocessing import Process
import pandas as pd
import numpy as np

###############################################################################


# host config -- you probably need to change this
# IP_CLIENT = "192.168.178.20"
# IFACE_CLIENT = "wlp4s0"
IP_CLIENT = "141.22.28.227"
IFACE_CLIENT = "eno1"

###############################################################################


# dns config sniff config -- you can leave it as is
QRY_NAME = "rr-mirror.research.nawrocki.berlin"
CLIENT_PORT = random.randrange(10000, 65500, 100) # 3 digit ID, 2 digits TTL
# default is 30, increase if necessary
MAX_TTL = 30
BPF_FILTER = f"ip dst {IP_CLIENT} and (src port 53 and dst port {CLIENT_PORT})"

# catch all ICMP responses (TTL exceeded)
BPF_FILTER =  f"ip dst {IP_CLIENT} and ((icmp and icmp[icmptype]==11) or"
# and DNS responses on the correct ports
BPF_FILTER += f" (udp and src port 53 and"
BPF_FILTER += f" dst portrange {CLIENT_PORT}-{CLIENT_PORT+MAX_TTL}))"

# result data -- passing a list enforces call by reference
responses = []

# stop indicator -- passing a list enforces call by reference
ALL_PKTS_SENT = [False]

###############################################################################


def send_dns_req(target, all_pkts_sent, per_hop=1, iface=IFACE_CLIENT,
                   max_ttl=MAX_TTL, qry_name=QRY_NAME):

    # wait for the sniffer to init
    sleep(2)

    # open socket which we can reuse for sending
    mySocket = conf.L3socket(iface=iface)

    # start sending all probes
    for tmp_ttl in range(max_ttl):
        for _ in range(per_hop):

            dns_req = IP(src=IP_CLIENT, dst=target, ttl=tmp_ttl)/\
                        UDP(sport=CLIENT_PORT+tmp_ttl, dport=53)/\
                        DNS(rd=1, id=RandShort(), qd=DNSQR(qname=qry_name))

            # sent packet by reusing existing socket
            mySocket.send(dns_req)

    # stop this worker (killing this worker also stops the sniffer process)
    sleep(3)
    all_pkts_sent[0] = True


###############################################################################


def parse_response(pkt, target, responses, max_ttl=MAX_TTL,
                    ip_client=IP_CLIENT, client_port=CLIENT_PORT):

    # we will only parse packets for which we have HOP/TTL information
    ts = datetime.utcnow()

    # its either appended as a fragment to the ICMP message
    if (ICMP in pkt and UDPerror in pkt and
        client_port <= pkt[UDPerror].sport <= client_port+max_ttl):

        responses.append([ pkt[UDPerror].sport%client_port, pkt[IP].src,
                           ts, ip_client, target, pkt.summary()])

    # or part of the normal UDP header from the DNS response
    if (DNS in pkt and pkt[DNS].qr == 1 and DNSQR in pkt and
        pkt[DNSQR].qname.decode().lower().startswith(QRY_NAME)):

        responses.append([ pkt[UDP].dport%client_port, pkt[IP].src,
                           ts, ip_client, target, pkt.summary()])

###############################################################################


# main entry point
if __name__ == "__main__":

    # parse arguments, if not supplied raise error
    if len(sys.argv) == 2:
        target = sys.argv[1].strip()
    else:
        print("# ERROR -- FIX ARGUMENTS")
        sys.exit(-1)

    # start prober application
    prober = Process(target=send_dns_req, args=(target, ALL_PKTS_SENT))
    prober.start()

    # start sniffing
    sniff(iface=IFACE_CLIENT, filter=BPF_FILTER, store=False,
            prn=lambda pkt: parse_response(pkt, target, responses),
            timeout=7,
            stop_filter=lambda _: ALL_PKTS_SENT[0] or not prober.is_alive())
    prober.terminate()
    prober.close()

    # create result frame
    columns = [ "hop.id", "ip.response", "ts.utc", "ip.scanner",
                "ip.target", "pkt.layers"]
    df = pd.DataFrame(responses, columns=columns)
    df = df.sort_values(by=["hop.id"], ascending=True)
    df.to_csv(f"logs/dnsroute_{target}.csv.gz", sep="|",
              header=False, index=False)
