

import argparse
import math
import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path

def parse_args():
    p = argparse.ArgumentParser(description="Parse SUMO FCD XML to CSVs with distance & speed alerts")
    p.add_argument("--in", dest="infile", default="fcd.xml",
                   help="FCD xml file (default: fcd.xml)")
    p.add_argument("--scenario-out", default="scenario.csv",
                   help="Output CSV for ego/lead scenario (default: scenario.csv)")
    p.add_argument("--all-out", default="fcd_all.csv",
                   help="Output CSV for all vehicles (default: fcd_all.csv)")
    p.add_argument("--alerts-out", default="alerts.csv",
                   help="Output CSV for alerts (default: alerts.csv)")
# make sure to keep the default values consistent with dump_via_traci.py
    p.add_argument("--min-gap-m", type=float, default=2.0,
                   help="最小静态安全间距（m），默认2.0")
    p.add_argument("--time-headway-s", type=float, default=1.5,
                   help="时间车头时距阈值（s），默认1.5")
    p.add_argument("--ttc-thresh-s", type=float, default=2.0,
                   help="TTC阈值（s），默认2.0；当相对速度>0且TTC小于该值时刹车")
    p.add_argument("--ego-len-m", type=float, default=5.0,
                   help="自车长度，用于一维x向间距修正（默认5m）")
    return p.parse_args()

def load_xml(path: str):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"FCD xml not found: {path.resolve()}")
    tree = ET.parse(str(path))
    return tree.getroot()

def build_ego_lead_table(root, ego_id="ego", lead_id="lead", ego_len_m=5.0):
    """
    构建“方法一”场景表：同一步存在 ego 和 lead 时，计算速度/车距/相对速度/TTC等。
    返回：DataFrame(columns:
        t_s, v_self_kmh, v_lead_kmh, lead_dist_m,
        rel_speed_kmh, rel_speed_mps, ttc_s,
        speed_limit_kmh, zone)
    """
    rows = []
    for ts in root.findall("timestep"):
        t = float(ts.attrib["time"])
        vmap = {}
        for veh in ts.findall("vehicle"):
            vid = veh.attrib.get("id", "")
            x = float(veh.attrib.get("x", "0"))
            y = float(veh.attrib.get("y", "0"))
            v_kmh = float(veh.attrib.get("speed", "0")) * 3.6
            vmap[vid] = {"x": x, "y": y, "v_kmh": v_kmh}

        if ego_id in vmap and lead_id in vmap:
            v_self = vmap[ego_id]["v_kmh"]
            v_lead = vmap[lead_id]["v_kmh"]

            # line distance，minus ego length
            lead_dist = vmap[lead_id]["x"] - vmap[ego_id]["x"] - ego_len_m
            lead_dist = max(lead_dist, 0.0)

            # speed diff
            rel_speed_kmh = v_self - v_lead
            rel_speed_mps = rel_speed_kmh / 3.6

            # TTC：rel_speed_mps>0
            if rel_speed_mps > 1e-6:
                ttc_s = lead_dist / rel_speed_mps if lead_dist > 0 else 0.0
            else:
                ttc_s = math.inf

            rows.append([
                t, v_self, v_lead, lead_dist,
                rel_speed_kmh, rel_speed_mps, ttc_s
            ])

    df = pd.DataFrame(rows, columns=[
        "t_s", "v_self_kmh", "v_lead_kmh", "lead_dist_m",
        "rel_speed_kmh", "rel_speed_mps", "ttc_s"
    ])

    
    if not df.empty:
        t_mid = df["t_s"].median()
        df["speed_limit_kmh"] = (df["t_s"] < t_mid).map({True: 80, False: 50})
        df["zone"] = (df["t_s"] < t_mid).map({True: "NORMAL", False: "SCHOOL"})

    return df

def build_all_vehicle_table(root):
    
    data = []
    for ts in root.findall("timestep"):
        t = float(ts.attrib.get("time", "0"))
        for veh in ts.findall("vehicle"):
            vid = veh.attrib.get("id", "")
            x = float(veh.attrib.get("x", "0"))
            y = float(veh.attrib.get("y", "0"))
            speed_kmh = float(veh.attrib.get("speed", "0")) * 3.6
            data.append([t, vid, x, y, speed_kmh])

    return pd.DataFrame(data, columns=["time_s", "id", "x_m", "y_m", "speed_kmh"])

def mark_brake_and_speeding(df_scene: pd.DataFrame,
                            min_gap_m: float,
                            time_headway_s: float,
                            ttc_thresh_s: float) -> pd.DataFrame:
   
    if df_scene.empty:
        df_scene["need_brake"] = False
        df_scene["brake_reason"] = ""
        df_scene["overspeed"] = False
        df_scene["target_speed_kmh"] = pd.NA
        return df_scene

    v_self_mps = df_scene["v_self_kmh"] / 3.6
    headway_need_m = min_gap_m + v_self_mps * time_headway_s

    cond_gap = df_scene["lead_dist_m"] < headway_need_m
    cond_ttc = df_scene["ttc_s"] < ttc_thresh_s

    need_brake = cond_gap | cond_ttc
    reason = []
    for g, ttc in zip(cond_gap, cond_ttc):
        if g and ttc:
            reason.append("GAP/HEADWAY + TTC")
        elif g:
            reason.append("GAP/HEADWAY")
        elif ttc:
            reason.append("TTC")
        else:
            reason.append("")

    df_scene = df_scene.copy()
    df_scene["need_brake"] = need_brake
    df_scene["brake_reason"] = reason

    if "speed_limit_kmh" in df_scene.columns:
        df_scene["overspeed"] = df_scene["v_self_kmh"] > df_scene["speed_limit_kmh"]
        df_scene["target_speed_kmh"] = df_scene[["v_lead_kmh", "speed_limit_kmh"]].min(axis=1)
    else:
        df_scene["overspeed"] = False
        df_scene["target_speed_kmh"] = df_scene["v_lead_kmh"]

    return df_scene

def emit_alerts(df_scene: pd.DataFrame, alerts_out: str):
   
    if df_scene.empty:
        pd.DataFrame(columns=["timestamp","kind","speed","distance","reason"]).to_csv(alerts_out, index=False)
        print(f"✅ Wrote {alerts_out} with 0 rows (empty scene)")
        return

    d = df_scene.sort_values("t_s").reset_index(drop=True)

    alerts = []
    prev_brake = False
    prev_speeding = False

    for i, row in d.iterrows():
        t = row["t_s"]
        v = row["v_self_kmh"]
        dist = row["lead_dist_m"]
        # brake 
        nb = bool(row["need_brake"])
        if nb and not prev_brake:
            alerts.append({
                "timestamp": t,
                "kind": "BRAKE",
                "speed": v,
                "distance": dist,
                "reason": f"{row['brake_reason']} (target≈{row['target_speed_kmh']:.1f} km/h)"
            })
        prev_brake = nb

        # overspeed
        spd = bool(row["overspeed"])
        if spd and not prev_speeding:
            lim = row["speed_limit_kmh"] if "speed_limit_kmh" in row else float("nan")
            alerts.append({
                "timestamp": t,
                "kind": "SPEEDING",
                "speed": v,
                "distance": dist,
                "reason": f"Speed {v:.2f} exceeds limit {lim:.2f}"
            })
        prev_speeding = spd

    pd.DataFrame(alerts, columns=["timestamp","kind","speed","distance","reason"]).to_csv(alerts_out, index=False)
    print(f"✅ Wrote {alerts_out} with {len(alerts)} rows")

def main():
    args = parse_args()
    root = load_xml(args.infile)

    # method one: ego-lead scenario table
    df_scene = build_ego_lead_table(root, ego_id="ego", lead_id="lead", ego_len_m=args.ego_len_m)

    # judge braking and speeding
    df_scene = mark_brake_and_speeding(
        df_scene,
        min_gap_m=args.min_gap_m,
        time_headway_s=args.time_headway_s,
        ttc_thresh_s=args.ttc_thresh_s
    )

    df_scene.to_csv(args.scenario_out, index=False)
    print(f"✅ Wrote {args.scenario_out} with {len(df_scene)} rows")

    # Alerts
    emit_alerts(df_scene, args.alerts_out)

    # method two: all vehicles FCD table
    df_all = build_all_vehicle_table(root)
    df_all.to_csv(args.all_out, index=False)
    print(f"✅ Wrote {args.all_out} with {len(df_all)} rows")

   
    if df_scene.empty:
        has_ego = (df_all["id"] == "ego").any() if not df_all.empty else False
        has_lead = (df_all["id"] == "lead").any() if not df_all.empty else False
        if not df_all.empty and (not has_ego or not has_lead):
            print("ℹ️  attention: did not find 'ego ' or 'lead' vehicle in FCD. Please confirm their IDs are indeed ego/lead.")
        elif df_all.empty:
            print("ℹ️  there is no vehicle record in FCD. Please confirm <fcd-output> is configured in sumo.sumocfg, and there are vehicles running in the network during the simulation.")

if __name__ == "__main__":
    main()
