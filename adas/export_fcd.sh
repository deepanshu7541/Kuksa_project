#!/bin/bash

echo "Running SUMO to generate FCD -> ./fcd.xml"

sumo \
    -n simple.net.xml \
    -r simple.rou.xml \
    --fcd-output fcd.xml \
    --step-length 0.1

echo "Done. FCD file exported -> fcd.xml"

# set -e

# echo "Running SUMO to generate FCD -> ./fcd.xml"

# sumo -c simple.sumocfg

# echo "Done. FCD generated as fcd.xml"