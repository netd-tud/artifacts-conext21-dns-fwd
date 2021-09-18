#!/bin/sh

echo "===== Test 1: Remote Resolver Default ====="
dig +short rr-mirror.research.nawrocki.berlin

echo "===== Test 2: Remote Resolver Quad9 ====="
dig +short rr-mirror.research.nawrocki.berlin @9.9.9.9

echo "===== Test 3: Local Resolver ====="
dig +short rr-mirror.research.nawrocki.berlin @ns.nawrocki.berlin.
