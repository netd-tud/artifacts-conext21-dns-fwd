# DNS Measurement Analysis

This directory contains:
1. [two example pcap files](https://github.com/ilabrg/artifacts-conext21-dns-fwd/tree/main/dns-measurement-analysis/raw_pcap_scan_data) of our scans
2. [two example csv.gz files](https://github.com/ilabrg/artifacts-conext21-dns-fwd/tree/main/dns-measurement-analysis/sanitized_csv_scan_data) which have passed the first postprocessing stage (matching outgoing requests with incoming responses)
3. a [postprocessed dataframe](https://github.com/ilabrg/artifacts-conext21-dns-fwd/tree/main/dns-measurement-analysis/dataframes) which has passed all postprocessing stages. This dataframe is not an excerpt, but contains the data of an complete IPv4 scan.
4. a [pyasn db with scripts](https://github.com/ilabrg/artifacts-conext21-dns-fwd/tree/main/dns-measurement-analysis/pyasn_db) to easily download the latest routeviews data for IP to AS mapping
5. [dataframes which allow AS to country-code(CC)](https://github.com/ilabrg/artifacts-conext21-dns-fwd/tree/main/dns-measurement-analysis/AS_2_CountryCode) mapping
6. Python and Bash scripts to sanitize the raw scan data
7. a jupyter-notebook file to run the analysis for the postprocessed dataframe as well as the notebook in HTML format

## Requirements

### Python Tools

This implementation is written in Python3. The non-default requirements are:

```python
matplotlib
pandas
numpy
seaborn
tqdm
pyasn
pycountry
bs4
requests
csv
```

### Shell Scripts

```bash
tshark
parallel
```

### Interface Settings

Adjust source IP address directly in the script:

```python
IP_CLIENT = "141.22.28.227"
```

## Compilation & Running

Install all dependencies. Then, simply execute the run command below.

```bash
./runscript.sh $ip  # configure interface in script
```

### Expected Output

The run script performs sanitation steps with the excerpt of the raw scan data and should produce new "dns_complete_*.csv.gz" files which are then passed further to map ASNs and country codes and finally produce a new dataframe which can be used in the jupyter-notebook to analyse the results.

