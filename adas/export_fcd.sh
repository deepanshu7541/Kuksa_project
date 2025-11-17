set -e

echo "Running SUMO to generate FCD -> ./fcd.xml"

sumo -c simple.sumocfg

echo "Done. FCD generated as fcd.xml"