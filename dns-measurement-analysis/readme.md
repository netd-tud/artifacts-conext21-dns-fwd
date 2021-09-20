# DNS Measurement Analysis

This directory contains real scan data from one of our scans and also python and shell scripts to process the data from raw pcap files to a clean dataframe used for the analysis.
This directory also provides a complete dataframe of our scan from April 20th, 2021. We only provide two pcap files of the scan to keep storage usage low.
The runscript can be used with your own scan results by simply replacing the right files as explained in section **Configuration of Runscript & Scan Data**.

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

## Configuration of Runscript & Scan Data

The ```run.sh``` file is preset to use our [two pcap files](https://github.com/ilabrg/artifacts-conext21-dns-fwd/tree/main/dns-measurement-analysis/raw_pcap_scan_data) of our scan from April 20th, 2021.
To execute the script using your own data just replace [the example pcap files](https://github.com/ilabrg/artifacts-conext21-dns-fwd/tree/main/dns-measurement-analysis/raw_pcap_scan_data) with your own data or replace the directory paths in ```run.sh```.
If you use your own data you also need to configure the interface IP address directly in the ```run.sh``` script in line 9 (second argument).

## Compilation & Running

### Preset Configuration with small Set of Scan Data
Install all dependencies. Then, simply execute the run command below.

```bash
./run.sh
```

#### Expected Output

The run script performs sanitation steps with the excerpt of the raw scan data and should produce new "dns_complete_*.csv.gz" files which are then passed further to map ASNs and country codes and finally produce a new dataframe in the dataframes directory which is than used to create the plots shown in the paper (can be found under ./figures).

### Produce Plots Using Complete Dataframe from April 20th, 2021

Install python dependencies. Then, simply execute the command below.
```python
python3 Paper_Plots.py ./dataframes/dataframe_complete_20210420.csv.gz
```

#### Expected Output

This script produces [the paper plots](https://github.com/ilabrg/artifacts-conext21-dns-fwd/tree/main/dns-measurement-analysis/figures) by using the complete dataframe of the scan from April 20th, 2021.
