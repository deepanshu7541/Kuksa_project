import xml.etree.ElementTree as ET
import csv
import sys
from pathlib import Path

def fcd_xml_to_csv(xml_path, csv_path):
    xml_path = Path(xml_path)
    tree = ET.parse(xml_path)
    root = tree.getroot()

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time_s","veh_id","x","y","speed"])
        for ts in root.findall("timestep"):
            t = float(ts.get("time"))
            for veh in ts.findall("vehicle"):
                vid = veh.get("id")
                x = veh.get("x")
                y = veh.get("y")
                speed = veh.get("speed")
                writer.writerow([t, vid, float(x) if x is not None else "", float(y) if y is not None else "", float(speed) if speed is not None else ""])

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python fcd_to_csv.py fcd.xml out.csv")
        sys.exit(1)
    fcd_xml_to_csv(sys.argv[1], sys.argv[2])
    print("Converted", sys.argv[1], "->", sys.argv[2])