# # import xml.etree.ElementTree as ET
# # import pandas as pd

# # tree = ET.parse("fcd.xml")
# # root = tree.getroot()


# # EGO_LEN = 5.0

# # rows = []
# # for ts in root.findall("timestep"):
# #     t = float(ts.attrib["time"])  # 秒
# #     vmap = {}
# #     for veh in ts.findall("vehicle"):
# #         vid = veh.attrib["id"]
# #         vmap[vid] = {
# #             "x": float(veh.attrib["x"]),
# #             "y": float(veh.attrib["y"]),
# #             "v_kmh": float(veh.attrib["speed"]) * 3.6
# #         }
# #     if "lead" in vmap and "ego" in vmap:
# #         v_lead = vmap["lead"]["v_kmh"]
# #         v_self = vmap["ego"]["v_kmh"]
       
# #         lead_dist = vmap["lead"]["x"] - vmap["ego"]["x"] - EGO_LEN
# #         rows.append([t, v_self, v_lead, max(lead_dist, 0.0)])

# # df = pd.DataFrame(rows, columns=["t_s","v_self_kmh","v_lead_kmh","lead_dist_m"])


# # if not df.empty:
# #     t_mid = df["t_s"].median()
# #     df["speed_limit_kmh"] = (df["t_s"] < t_mid).map({True:80, False:50})
# #     df["zone"] = (df["t_s"] < t_mid).map({True:"NORMAL", False:"SCHOOL"})

# # df.to_csv("scenario.csv", index=False)
# # print("Wrote scenario.csv with", len(df), "rows")


# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# import argparse
# import xml.etree.ElementTree as ET
# import pandas as pd
# from pathlib import Path

# def parse_args():
#     p = argparse.ArgumentParser(description="Parse SUMO FCD XML to CSVs")
#     p.add_argument("--in", dest="infile", default="fcd.xml",
#                    help="FCD xml file (default: fcd.xml)")
#     p.add_argument("--scenario-out", default="scenario.csv",
#                    help="Output CSV for ego/lead scenario (default: scenario.csv)")
#     p.add_argument("--all-out", default="fcd_all.csv",
#                    help="Output CSV for all vehicles (default: fcd_all.csv)")
#     return p.parse_args()

# def load_xml(path: str):
#     path = Path(path)
#     if not path.exists():
#         raise FileNotFoundError(f"FCD xml not found: {path.resolve()}")
#     tree = ET.parse(str(path))
#     return tree.getroot()

# def build_ego_lead_table(root, ego_id="ego", lead_id="lead", ego_len_m=5.0):
#     """
#     构建你的“方法一”场景表：同一步存在 ego 和 lead 时，计算速度/车距。
#     返回：DataFrame(columns: t_s, v_self_kmh, v_lead_kmh, lead_dist_m, zone/speed_limit_kmh 可选)
#     """
#     rows = []
#     for ts in root.findall("timestep"):
#         t = float(ts.attrib["time"])
#         vmap = {}
#         for veh in ts.findall("vehicle"):
#             vid = veh.attrib["id"]
#             # 有些 FCD 会缺某些属性，这里做个兜底
#             x = float(veh.attrib.get("x", "0"))
#             y = float(veh.attrib.get("y", "0"))
#             v_kmh = float(veh.attrib.get("speed", "0")) * 3.6
#             vmap[vid] = {"x": x, "y": y, "v_kmh": v_kmh}

#         if ego_id in vmap and lead_id in vmap:
#             v_self = vmap[ego_id]["v_kmh"]
#             v_lead = vmap[lead_id]["v_kmh"]
#             # 只用 x 方向估算前后距离（一维直线场景）
#             lead_dist = vmap[lead_id]["x"] - vmap[ego_id]["x"] - ego_len_m
#             rows.append([t, v_self, v_lead, max(lead_dist, 0.0)])

#     df = pd.DataFrame(rows, columns=["t_s", "v_self_kmh", "v_lead_kmh", "lead_dist_m"])
#     if not df.empty:
#         # 你的“方法一”里对半切 zone/speed_limit 的逻辑也保留
#         t_mid = df["t_s"].median()
#         df["speed_limit_kmh"] = (df["t_s"] < t_mid).map({True: 80, False: 50})
#         df["zone"] = (df["t_s"] < t_mid).map({True: "NORMAL", False: "SCHOOL"})
#     return df

# def build_all_vehicle_table(root):
#     """
#     方法二：通用 FCD 明细，每个 timestep × 每辆车一行。
#     返回：DataFrame(columns: time, id, x, y, speed_kmh)
#     """
#     data = []
#     for ts in root.findall("timestep"):
#         t = float(ts.attrib.get("time", "0"))
#         for veh in ts.findall("vehicle"):
#             vid = veh.attrib.get("id", "")
#             x = float(veh.attrib.get("x", "0"))
#             y = float(veh.attrib.get("y", "0"))
#             speed_kmh = float(veh.attrib.get("speed", "0")) * 3.6
#             data.append([t, vid, x, y, speed_kmh])

#     return pd.DataFrame(data, columns=["time_s", "id", "x_m", "y_m", "speed_kmh"])

# def main():
#     args = parse_args()
#     root = load_xml(args.infile)

#     # 方法一：ego/lead 场景表
#     df_scene = build_ego_lead_table(root, ego_id="ego", lead_id="lead", ego_len_m=5.0)
#     df_scene.to_csv(args.scenario_out, index=False)
#     print(f"✅ Wrote {args.scenario_out} with {len(df_scene)} rows")

#     # 方法二：通用明细表（总会导出，便于排查 0 行问题）
#     df_all = build_all_vehicle_table(root)
#     df_all.to_csv(args.all_out, index=False)
#     print(f"✅ Wrote {args.all_out} with {len(df_all)} rows")

#     # 友好提示：如果 scenario 是 0 行，看看 all 表里有没有 ego/lead
#     if df_scene.empty:
#         has_ego = (df_all["id"] == "ego").any() if not df_all.empty else False
#         has_lead = (df_all["id"] == "lead").any() if not df_all.empty else False
#         if not df_all.empty and (not has_ego or not has_lead):
#             print("ℹ️  注意：在 FCD 中未找到 'ego' 或 'lead' 车辆。请确认它们的车辆ID是否真的叫 ego/lead。")
#         elif df_all.empty:
#             print("ℹ️  FCD 里一个车辆记录都没有。请确认 sumo.sumocfg 已配置 <fcd-output>，且仿真期间有车辆在路网中运行。")

# if __name__ == "__main__":
#     main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
    # 可调参数（如需更激进/保守的刹车逻辑，可在命令行传入）
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

            # 一维直线场景（同车道）使用x向距离并扣除自车长度
            lead_dist = vmap[lead_id]["x"] - vmap[ego_id]["x"] - ego_len_m
            lead_dist = max(lead_dist, 0.0)

            # 相对速度：自车-前车（>0表示在逼近）
            rel_speed_kmh = v_self - v_lead
            rel_speed_mps = rel_speed_kmh / 3.6

            # TTC：rel_speed_mps>0 才有逼近，避免除零/负值
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

    # 分区限速（保留你原逻辑：前半程80，后半程50）
    if not df.empty:
        t_mid = df["t_s"].median()
        df["speed_limit_kmh"] = (df["t_s"] < t_mid).map({True: 80, False: 50})
        df["zone"] = (df["t_s"] < t_mid).map({True: "NORMAL", False: "SCHOOL"})

    return df

def build_all_vehicle_table(root):
    """
    方法二：通用 FCD 明细，每个 timestep × 每辆车一行。
    返回：DataFrame(columns: time_s, id, x_m, y_m, speed_kmh)
    """
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
    """
    在场景表上增加规则判定列：
      - need_brake：是否需要刹车
      - brake_reason：'GAP/HEADWAY' 或 'TTC'
      - overspeed：是否超速
      - target_speed_kmh：建议目标速度（取 min(前车速度, 限速)）
    """
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
    """
    生成 alerts.csv：
      kind: 'BRAKE' 或 'SPEEDING'
      speed: 当前自车速度
      distance: 车距
      reason: 文本说明
    去抖：仅在状态从 False->True 的过渡时写一条
    """
    if df_scene.empty:
        pd.DataFrame(columns=["timestamp","kind","speed","distance","reason"]).to_csv(alerts_out, index=False)
        print(f"✅ Wrote {alerts_out} with 0 rows (empty scene)")
        return

    # 先按时间排序（以防输入无序）
    d = df_scene.sort_values("t_s").reset_index(drop=True)

    alerts = []
    prev_brake = False
    prev_speeding = False

    for i, row in d.iterrows():
        t = row["t_s"]
        v = row["v_self_kmh"]
        dist = row["lead_dist_m"]
        # 刹车事件
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

        # 超速事件
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

    # 方法一：ego/lead 场景表
    df_scene = build_ego_lead_table(root, ego_id="ego", lead_id="lead", ego_len_m=args.ego_len_m)

    # 判定刹车 + 超速
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

    # 方法二：通用明细表（总会导出，便于排查 0 行问题）
    df_all = build_all_vehicle_table(root)
    df_all.to_csv(args.all_out, index=False)
    print(f"✅ Wrote {args.all_out} with {len(df_all)} rows")

    # 友好提示：如果 scenario 是 0 行，看看 all 表里有没有 ego/lead
    if df_scene.empty:
        has_ego = (df_all["id"] == "ego").any() if not df_all.empty else False
        has_lead = (df_all["id"] == "lead").any() if not df_all.empty else False
        if not df_all.empty and (not has_ego or not has_lead):
            print("ℹ️  注意：在 FCD 中未找到 'ego' 或 'lead' 车辆。请确认它们的车辆ID是否真的叫 ego/lead。")
        elif df_all.empty:
            print("ℹ️  FCD 里一个车辆记录都没有。请确认 sumo.sumocfg 已配置 <fcd-output>，且仿真期间有车辆在路网中运行。")

if __name__ == "__main__":
    main()
