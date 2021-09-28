# DNS Scan Server

This directory contains all the necessary scripts to actually execute a scan of the complete IPv4 address space.

## Setup and Recommendation

Our sub-prefix does not have any traffic filters upstream.
We recommend this for limitless scanning, otherwise you might run into trouble doing a complete IPv4 scan.


## Requirements

Overall, this artifact is a wrapper script for multiple well-known tools. We initiate a `screen` session with multiple tabs.

We use `zmap` for scans. Get it e.g. [here](https://github.com/zmap/zmap). We utilize the `DNS` module for scanning which is not shipped in some `zmap` packages, therefore we recommend compiling from source. Currently, the DNS module appears to be broken, please use the following commit:

```bash
git clone https://github.com/zmap/zmap.git
git checkout 623d069
# install as described in zmaps INSTALL.md
```

We use `dumpcap` to capture all outgoing and incoming traffic.
You can get `dumpcap` e.g. by installing `wireshark` on your system.

For convenience, this script also shows traffic statistics with `bmon`.

## Configuration & Running

### Zmap Wrapper Scripts

The main script can be executed as follows: 
```
# perform complete IPv4 address space DNS scan
screen -c complete.screenrc
# perform a IPv4 DNS scan which is limitied to IP in a configfile
screen -c limited.screenrc
```

Within the screen session, you can change between the tabs with `ctrl-a n`.
Please check the tabs in ascending order (left to right), enter sudo password if necessary.

#### Tab 1: Bash

Simple `bash` tab for misc commands.

#### Tab 2: Bmon

The network monitor `bmon` shows on-going statistics like `pps` (packets per second) etc. 

#### Tab 4: DumpCap

This tab starts a dumpcap process which saves pcap-files in the folder `pcaps_dns_complete` or `pcaps_dns_limited`, depending on the scan-type.
Dumpcap splits the pcaps into 100mb chunks (configurable).

After the zmap scan finished (next tab), just `ctrl-c` this tab.

#### Tab 5: Zmap DNS Scan

This is a script which runs a self-compiled zmap version.
The repository version of zmap does not include the DNS module, that is why you have to install it manually.

```
# run zmap
if [[ "$mode" == "complete" ]]; then
    zmap \
        --interface="$interface" \
        --source-ip="$node_ip" \
        --target-port=53 \
        --probe-module=dns \
        --probe-args="$dns_request_complete" \
        --seed=13371337 \
        --blocklist-file=/etc/zmap/blocklist.conf \
        --rate=55000 \
        -O json -o $logfile \
        --output-fields="saddr" \
        --output-filter="success = 1 && app_success = 1"
```

This config use multiple variables which are loaded from the `config_file` in the same directory.
For your complete scan, double check that these variables are set correctly and replace interface name and node IP address if necessary:

```
interface="eno1"
node_ip="141.22.28.227"
dns_request_complete="A,rr-mirror.research.nawrocki.berlin"
```

The current config need ~20 hours.
We choose a static scanning seed so that IP addresses are always scanned in the same order if you need to repeat your measurements.



