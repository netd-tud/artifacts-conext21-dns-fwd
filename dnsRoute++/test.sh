#!/bin/bash

for ip in $(zcat ip_list.txt.gz);
do
    if grep -qi "TRUE" <(./isTranspFwd.sh $ip); then
        echo "$(date -I'seconds' -u)|$ip|dnsRoute"
	./dnsRoute++.py $ip
    else
        echo "$(date -I'seconds' -u)|$ip|skip"
    fi
done
