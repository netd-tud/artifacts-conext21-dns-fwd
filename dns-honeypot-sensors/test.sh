#!/bin/sh

echo "===== Test 1: proxy @91.216.216.51 ====="
dig +unexpected google.com A @91.216.216.51 | grep -A1 ";; ANSWER\|;; SERVER"

echo "===== Test 2: localfwd @91.216.216.52 ====="
dig +unexpected google.com A @91.216.216.52 | grep -A1 ";; ANSWER\|;; SERVER"

echo "===== Test 3: remotefwd @91.216.216.54 ====="
dig +unexpected google.com A @91.216.216.54 | grep -A1 ";; ANSWER\|;; SERVER"
