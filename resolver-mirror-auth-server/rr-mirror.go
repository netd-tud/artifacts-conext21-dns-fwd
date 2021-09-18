package main

import (
    "log"
    "strconv"
    "net"
    "strings"
    "github.com/miekg/dns"
)

var records = map[string]bool{
    "rr-mirror.research.nawrocki.berlin.": true,
}

// will only answer A queries for names in records dict
func mirrorResolver(req *dns.Msg, rr_ip string) *dns.Msg {

    for _, q := range req.Question {
        switch q.Qtype {
        case dns.TypeA:
            if records[strings.ToLower(q.Name)] {

                response := new(dns.Msg)
                response.SetReply(req)
                response.Authoritative = true

                rr_a := &dns.A {
                            Hdr: dns.RR_Header {
                                Name: q.Name,
                                Rrtype: dns.TypeA,
                                Class: dns.ClassINET,
                                Ttl: 3600 },
                            A: net.ParseIP(rr_ip),
		    }
                response.Answer = append(response.Answer, rr_a)
		//include a second static A record to distinguish DNS manipulations during scans
                rr_a_static := &dns.A {
                            Hdr: dns.RR_Header {
                                Name: q.Name,
                                Rrtype: dns.TypeA,
                                Class: dns.ClassINET,
                                Ttl: 3600 },
                            A: net.ParseIP("91.216.216.216"), }
                response.Answer = append(response.Answer, rr_a_static)

                log.Printf("%s %s\n", q.Name, rr_ip)

                return response
            }
        }
    }
    return nil
}

// drops all requests silently but for our records dict entries
func handleDnsRequest(w dns.ResponseWriter, req *dns.Msg) {

    switch req.Opcode {
    case dns.OpcodeQuery:
        rr_ip := w.RemoteAddr().(*net.UDPAddr).IP.String()
        response := mirrorResolver(req, rr_ip)
        if response != nil {
            w.WriteMsg(response)
        }
    }
}

func main() {

    // server config
    // server_ip := "127.0.0.1"
    // server_port := 53053
    server_ip := "141.22.213.44"
    server_port := 53
    server_zone := "."

    // attach request handler func
    dns.HandleFunc(server_zone, handleDnsRequest)

    // start server
    server := &dns.Server{
                Addr: server_ip +":"+ strconv.Itoa(server_port),
                Net: "udp"}
    log.Printf("Starting DNS mirror at %d\n", server_port)
    err := server.ListenAndServe()

    // catch errors and shutdown
    defer server.Shutdown()
    if err != nil {
        log.Fatalf("Failed to start server: %s\n ", err.Error())
    }
}
