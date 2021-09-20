#!/bin/bash
mode=$1
vp=$2
logdir="logs"
mkdir -p "${logdir}/${mode}"

python3 -u ./forwarder.py "$mode" "$vp" | tee "./${logdir}/${mode}/$(date "+%s").log"
