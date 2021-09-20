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
4. `dns-scan-server`: Server with no upstream filters to execute complete IPv4 address space scans.
5. `dns-measurement-analysis`: Postprocessing and analysing raw scan data.
 
### Minimal Test Setups

Each tool contains a test script which allows to evaluate each artifact with a minimal setup:

1. `dnsRoute++`: [Configure the interface](https://github.com/ilabrg/artifacts-conext21-dns-fwd/blob/main/dnsRoute++/readme.md#interface-settings), then [execute the run script in hitlist mode](https://github.com/ilabrg/artifacts-conext21-dns-fwd/blob/main/dnsRoute++/readme.md#hitlist-measurements) as root.
2. `dns-honeypot-sensors`: We offer test servers, so you can immediately [initiate the tests](https://github.com/ilabrg/artifacts-conext21-dns-fwd/tree/main/dns-honeypot-sensors#testing) as a normal user.
3. `recursive-mirror-auth-server`: We offer test servers, so you can immediately [initiate the tests](https://github.com/ilabrg/artifacts-conext21-dns-fwd/tree/main/resolver-mirror-auth-server#testing) as a normal user.
4. `dns-scan-server`: A server with no upstream filters is recommended, then [run the screen session](https://github.com/ilabrg/artifacts-conext21-dns-fwd/tree/main/dns-scan-server#zmap-wrapper-scripts)
5. `dns-measurement-analysis`: Configure the interface if necessary, then [run the test script](https://github.com/ilabrg/artifacts-conext21-dns-fwd/tree/main/dns-measurement-analysis#preset-configuration-with-small-set-of-scan-data).
