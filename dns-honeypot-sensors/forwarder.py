#! /usr/bin/env python3
###############################################################################

# libs
from scapy.all import Ether, IP, UDP, sniff, bind_layers, srp1, RandShort
from scapy.all import DNS, DNSQR, DNSRR, conf
from datetime import datetime
from multiprocessing import Process, SimpleQueue, cpu_count
from cachetools import TTLCache
import sys


###############################################################################

# config
debug = False # answers only for our name, lower rate limits
strict_dns = True # checks incoming DNS messages for expected field values
modes = ["proxy", "localfwd", "remotefwd"]
mode = modes[0]  # default mode
vp_list = ["ixp"]
vp = vp_list[0]  # default vp

prefixes = {
        "ixp": "91.216.216"
    }
prefix = prefixes[vp]

# interface which is used for incoming client requests and answers to clients
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

# use different vlan interface configs for different modes!

# public resolvers -- we use Q8 since it is the most common in our scans
RESOLVER_LIST = {
        "Q1": "1.1.1.1",
        "Q8": "8.8.8.8",
        "Q9": "9.9.9.9",
    }
RESOLVER_IP = RESOLVER_LIST["Q8"]

# sniffing stuff
DNS_PORT = 53
DNS_DEBUG_NAME = "forwarder.nawrocki.berlin"
N_WORKERS = cpu_count()-1

# rate limit per /24 prefix
p24_ttl = 10 if debug else 300
p24_cache = TTLCache(maxsize=100000, ttl=p24_ttl)


###############################################################################

def create_dns_response_record(pkt):

    # some variables and logging
    req_ipid = pkt[IP].id
    req_txid = pkt[DNS].id
    req_src = pkt[IP].src
    req_qname = pkt[DNSQR].qname
    req_sport = pkt[UDP].sport

    if mode == "proxy" or mode == "localfwd":

        # get real answer from resolver
        # https://scapy.readthedocs.io/en/latest/usage.html
        # https://github.com/secdev/scapy/issues/870
        # hacky: use srp1 and ETHER() so that we control outgoing interface
        hidden_req = Ether()/\
                     IP(src=DNS_SERVER_IP_DNS, dst=RESOLVER_IP)/\
                     UDP(sport=RandShort(), dport=DNS_PORT)/\
                     pkt[DNS]

        resolver_resp = srp1(hidden_req, timeout=3, retry=0,
                             verbose=1 if debug else 0,
                             iface=DNS_SERVER_IFACE_DNS)

        # make it look like our answer and get rid of ETHERNET workaround
        if resolver_resp is not None and DNS in resolver_resp:

            resp = IP(src=DNS_SERVER_IP_OUT, dst=req_src)/\
                   UDP(sport=DNS_PORT, dport=req_sport)/\
                   resolver_resp[DNS]

            print(f"{datetime.utcnow()}|{req_src}|{req_ipid}|" +
                  f"{req_sport}|{req_txid}|{req_qname}")
            return resp

    elif mode == "remotefwd":

        # we just forward the packet and make sure checksum are ok
        fwd_req = IP(src=req_src, dst=RESOLVER_IP)/\
                  UDP(sport=req_sport, dport=DNS_PORT)/\
                  pkt[DNS]

        print(f"{datetime.utcnow()}|{req_src}|{req_ipid}|" +
              f"{req_sport}|{req_txid}|{req_qname}")
        return fwd_req

    else:
        pass

    return None


###############################################################################

# detect incoming dns requests and respond
def dns_responder(pktQueue):

    try:
        mySocket = conf.L3socket(iface=DNS_SERVER_IFACE_OUT)

        while True:

            pkt = pktQueue.get()

            # we only care about DNS
            if not DNS in pkt:
                continue

            # if debug activated, only react to our name
            if (
                debug and not
                pkt[DNSQR].qname.decode().lower().startswith(DNS_DEBUG_NAME)
            ):
                continue

            # only react to DNS queries which look legitemate
            if strict_dns and not (
                pkt[DNS].qr == 0 and
                pkt[DNS].rd == 1 and
                pkt[DNS].opcode == 0 and
                pkt[DNS].qdcount == 1 and pkt[DNS].ancount == 0 and
                pkt[DNSQR].qclass == 1
            ):
                continue

            # prepare response for request
            resp = create_dns_response_record(pkt)

            # send pkt and inform about it
            if resp is not None:
                mySocket.send(resp)

    except KeyboardInterrupt:
        print("#Keyboard interrupt -- stopping responder.")
        pass


###############################################################################

# check rate limit for source, respond if ok
# this is run in a single thread, so potententially a bottleneck
# but scapy packet creation is more expensive and cache not threadsafe
def rate_limit_ok(pkt, myCache=p24_cache):

    p24_src = pkt["IP"].src.rstrip("0123456789")

    if p24_src in myCache:
        return False
    else:
        myCache[p24_src] = True
        return True


###############################################################################

# https://github.com/secdev/scapy/issues/870
# test with:
#   dig +tries=1 +timeout=3 forwarder.nawrocki.berlin @141.22.213.51

# main entry point
if __name__ == "__main__":

    # get mode for forwarder, set ifaces and ip addresses
    # all meta prints have '#' prefix
    if len(sys.argv) == 1:
        print(f"# Init in mode {mode}, debug {debug}, strictDNS {strict_dns}, vp {vp}.")
    elif len(sys.argv)==3 and sys.argv[1] in modes and sys.argv[2] in vp_list:
        mode = sys.argv[1]
        vp = sys.argv[2]
        print(f"# Init in mode {mode}, debug {debug}, strictDNS {strict_dns}, vp {vp}.")
    else:
        sys.exit(-1)

    DNS_SERVER_IFACE_IN, DNS_SERVER_IP_IN = ifaces[(mode,vp,"in")]
    DNS_SERVER_IFACE_DNS, DNS_SERVER_IP_DNS = ifaces[(mode,vp,"dns")]
    DNS_SERVER_IFACE_OUT, DNS_SERVER_IP_OUT = ifaces[(mode,vp,"out")]
    BPF_FILTER = f"not icmp and ip dst {DNS_SERVER_IP_IN}"
    BPF_FILTER += f" and udp and dst port {DNS_PORT}"

    # register dns parsing on dns port
    bind_layers(UDP, DNS, dport=DNS_PORT)
    pktQueue = SimpleQueue()

    # start multithreaded workers that wait for new packets
    for _ in range(N_WORKERS):
        Process(target=dns_responder, args=(pktQueue,)).start()

    # start sniffing, puts packets in queue bases on bpf filter and rate limit
    sniff(iface=DNS_SERVER_IFACE_IN, filter=BPF_FILTER, store=False,
          prn=lambda pkt: pktQueue.put(pkt) if rate_limit_ok(pkt) else None)
