#!/bin/bash

today=$(date +"%Y-%m-%d")

python3 pyasn_util_download.py --latestv46

find rib*.bz2 > .rib_files.txt

while read file; do
        python3 pyasn_util_convert.py --compress --single "$file" "ipasn-$today" 
done < .rib_files.txt

mv rib*.bz2 ./RIB/
mv ipasn*.gz ./IPASN/
