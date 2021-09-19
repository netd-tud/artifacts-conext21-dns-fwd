#!/bin/bash

ip=$1
name="rr-mirror.research.nawrocki.berlin"

if grep -qi "UNEXPECTED SOURCE" <(dig $name "@$ip" +notcp +novc +tries=1 +timeout=4); then
    echo "$ip|True"
else
    echo "$ip|False"
fi
