#!/bin/bash
mode=$1
logdir="logs"
mkdir -p "${logdir}/${mode}"

python3 -u ./forwarder.py "$mode" | tee "./${logdir}/${mode}/$(date "+%s").log"
