#!/bin/bash

if [ -z "$1" ]
then

    echo "No IP address -- Initiating Scan with hitlist."

    for ip in $(zcat ip_list.txt.gz);
    do
        if grep -qi "TRUE" <(./isTranspFwd.sh $ip); then
            echo "$(date -I'seconds' -u)|$ip|dnsRoute"
        ./dnsRoute++.py $ip
        else
            echo "$(date -I'seconds' -u)|$ip|skip"
        fi
    done

else
    echo "IP address found -- Initiating single host scan."
    if grep -qi "TRUE" <(./isTranspFwd.sh $1); then
        echo "$(date -I'seconds' -u)|$1|dnsRoute"
        ./dnsRoute++.py $1
    else
        echo "$(date -I'seconds' -u)|$1|skip"
    fi
fi
