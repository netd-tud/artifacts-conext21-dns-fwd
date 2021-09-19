# Artifacts - Transparent DNS Forwarders

This repository contains the artifacts for the following paper:

    Transparent Forwarders: An Unnoticed Component of the Open DNS Infrastructure.
    Authors anonymized.
    CoNEXT ’21, December 6–10, 2021, Virtual Event, USA.

## Structure

We include tools, which can be reused for follow-up measurements as well as raw data and analysis scripts to reproduce our results. Each sub-directory includes information on requirements, compilation, running and testing.

This repository is structured as follows:

1. `dnsRoute++`: Traceroute implementation which maps paths *behind* transparent forwarders.
2. `dns-honeypot-sensors`: Honeypots emulating various Open DNS speakers (ODNS), including transparent forwarders.
3. `recursive-mirror-auth-server`: DNS nameserver which replies with the IP address of the querist, revealing the recursive resolver.

### Minimal Test Setups

Each tool contains a test script which allows to test each artifact with a minimal setup.
1. `dnsRoute++`: [Configure the interface](https://github.com/ilabrg/artifacts-conext21-dns-fwd/blob/main/dnsRoute++/readme.md#interface-settings), then [run the test script for large measurement](https://github.com/ilabrg/artifacts-conext21-dns-fwd/blob/main/dnsRoute++/readme.md#large-scale-measurements).
