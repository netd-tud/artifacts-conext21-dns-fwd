# PYASN Database
This toolchain downloads the latest routeview bgpdata and converts it into an PYASN Database.
The scripts are taken from https://github.com/hadiasghari/pyasn.git , the pyasn GIT repository.
They provide these scripts in the pyasn-utils/ directory.
## Requirements
### Python Tools
This implementation is written in Python3 and has no non-default requirements.

## Compilation & Running
Simply execute the run command below.

```bash
./get_latest_pyasn.sh
```
## Results
After executing the run command, the raw routeviews data can be found in ./RIB/ and the latest ASN database can be found in ./IPASN/ .
