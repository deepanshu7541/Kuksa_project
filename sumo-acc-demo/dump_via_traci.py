# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# import os
# import csv
# from pathlib import Path

# # ====== 请按你的路径调整 sumo 可执行文件 ======
# SUMO_BIN = "/Users/chaomeng/sumo-install/bin/sumo"  # 你的 sumo 路径

# CFG_FILE = "sumo.sumocfg"  # 也可以改为用 -n/-r 方式启动，见下方 alt_cmd
# OUT_CSV  = Path("outputs/fcd_traci.csv")

# def main():
#     # 准备输出目录
#     OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

#     # 方式A：用 cfg 启动
#     cmd = [SUMO_BIN, "-c", CFG_FILE, "--step-length", "1"]

#     # 方式B：不用 cfg，直接给 net / routes（若你愿意换这一行，注释掉上面的方式A）
#     # cmd = [SUMO_BIN, "-n", "road.net.xml", "-r", "routes.rou.xml", "--begin", "0", "--end", "200", "--step-length", "1"]

#     # 延迟导入，避免没装 traci 时出错
#     import traci

#     # 启动仿真
#     traci.start(cmd)

#     # 打开 CSV
#     with OUT_CSV.open("w", newline="") as f:
#         writer = csv.writer(f)
#         writer.writerow(["time_s", "veh_id", "x_m", "y_m", "speed_kmh"])

#         # 主循环：直到仿真结束
#         while traci.simulation.getMinExpectedNumber() > 0:
#             traci.simulationStep()
#             t = traci.simulation.getTime()  # 当前时间（秒）

#             for vid in traci.vehicle.getIDList():
#                 x, y = traci.vehicle.getPosition(vid)
#                 v_ms = traci.vehicle.getSpeed(vid)
#                 writer.writerow([t, vid, x, y, v_ms * 3.6])

#     traci.close()
#     print(f"✅ Wrote {OUT_CSV} (via TraCI)")

# if __name__ == "__main__":
#     # 基本的存在性检查（可选）
#     if not Path(SUMO_BIN).exists():
#         raise SystemExit(f"SUMO binary not found at: {SUMO_BIN}")
#     # cfg/net/routes 至少有一个存在
#     if not Path("sumo.sumocfg").exists() and not (Path("road.net.xml").exists() and Path("routes.rou.xml").exists()):
#         raise SystemExit("Missing sumo.sumocfg or (road.net.xml + routes.rou.xml)")
#     main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import math
import time
from pathlib import Path

# ====== 请按你的路径调整 sumo 可执行文件 ======
SUMO_BIN = "/Users/chaomeng/sumo-install/bin/sumo"  # 你的 sumo 路径

CFG_FILE = "sumo.sumocfg"  # 也可以改为用 -n/-r 方式启动，见下方 alt_cmd
OUT_CSV  = Path("outputs/fcd_traci.csv")
ALERTS_CSV = Path("outputs/alerts.csv")

# ====== 可调参数（根据需要改）======
STEP_LENGTH_S = 1.0               # 仿真 step
SPEED_LIMIT_KMH = 60.0            # 超速检测的限速（示例）
OVERSPEED_TOL_KMH = 5.0           # 容忍的超速浮动
SLOWDOWN_DURATION_S = 2.0         # 触发减速时，缓降到目标速度所用时间
MIN_GAP_M = 10.0                  # 距离过近阈值（米）
GAP_HYSTERESIS = 2.0              # 解除刹车的回程（避免抖动）
LEADER_LOOKAHEAD = 200.0          # 向前查找领导车的距离（米）
ALERT_COOLDOWN_S = 2.0            # 同一车辆同一告警的冷却时间（秒）

# ====== 内部状态（去重/节流用）======
last_alert_time = {}  # key=(veh_id, kind) -> sim_time
brake_active = {}     # key=veh_id -> bool

def now_ok_to_alert(veh_id, kind, t):
    k = (veh_id, kind)
    last = last_alert_time.get(k, -1e9)
    if t - last >= ALERT_COOLDOWN_S:
        last_alert_time[k] = t
        return True
    return False

def kmh_to_ms(v):
    return v / 3.6

def ms_to_kmh(v):
    return v * 3.6

def write_alert(writer, t, kind, subject, details):
    writer.writerow([t, kind, subject, details])

def main():
    # 准备输出目录
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    # 方式A：用 cfg 启动
    cmd = [SUMO_BIN, "-c", CFG_FILE, "--step-length", str(STEP_LENGTH_S)]

    # 方式B：不用 cfg，直接给 net / routes（若你愿意换这一行，注释掉上面的方式A）
    # cmd = [SUMO_BIN, "-n", "road.net.xml", "-r", "routes.rou.xml", "--begin", "0", "--end", "200", "--step-length", str(STEP_LENGTH_S)]

    # 延迟导入，避免没装 traci 时出错
    import traci

    # 启动仿真
    traci.start(cmd)

    # 打开 CSV
    with OUT_CSV.open("w", newline="") as f_fcd, ALERTS_CSV.open("w", newline="") as f_alerts:
        fcd_writer = csv.writer(f_fcd)
        alert_writer = csv.writer(f_alerts)

        fcd_writer.writerow(["time_s", "veh_id", "x_m", "y_m", "speed_kmh"])
        alert_writer.writerow(["time_s", "kind", "subject", "details"])

        # 主循环：直到仿真结束
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            t = traci.simulation.getTime()  # 当前时间（秒）

            veh_ids = list(traci.vehicle.getIDList())

            # === 1) 记录 FCD ===
            for vid in veh_ids:
                x, y = traci.vehicle.getPosition(vid)
                v_ms = traci.vehicle.getSpeed(vid)
                fcd_writer.writerow([t, vid, x, y, ms_to_kmh(v_ms)])

            # === 2) 车距检测 + 自动刹车 ===
            # 思路：对每辆车，查询其前车与间距；间距 < MIN_GAP -> 触发慢速；间距 > MIN_GAP + GAP_HYSTERESIS -> 解除
            for vid in veh_ids:
                try:
                    # (leader_id, gap) ; gap = front bumper distance (m)
                    leader = traci.vehicle.getLeader(vid, LEADER_LOOKAHEAD)
                except traci.TraCIException:
                    leader = None

                if not leader:
                    # 前面没人；如果之前有刹车状态，可选择放开限速（这里不强制放开，维持 SUMO 自己的车速控制）
                    brake_active[vid] = False
                    continue

                leader_id, gap_m = leader
                # 目标：保持安全距离
                if gap_m < MIN_GAP_M:
                    # 目标速度设为：min(当前, 领导车速度 - 小裕度)
                    try:
                        v_leader_ms = traci.vehicle.getSpeed(leader_id)
                    except traci.TraCIException:
                        v_leader_ms = kmh_to_ms(SPEED_LIMIT_KMH)  # 兜底

                    # 让当前车速度不高于前车，稍微再低一点避免贴死
                    target_ms = max(0.0, v_leader_ms - 1.0)

                    # 执行缓降
                    traci.vehicle.slowDown(vid, target_ms, int(SLOWDOWN_DURATION_S * 1000))
                    if now_ok_to_alert(vid, "DISTANCE_CLOSE", t):
                        write_alert(
                            alert_writer, t, "DISTANCE_CLOSE", vid,
                            f"gap={gap_m:.2f}m < {MIN_GAP_M:.2f}m; target={ms_to_kmh(target_ms):.1f}km/h"
                        )
                    brake_active[vid] = True
                else:
                    # gap 足够大，有回程则解除“强制慢速”的状态提示（不强制加速，以免与 SUMO 的 car-following 模型打架）
                    if brake_active.get(vid, False) and gap_m > MIN_GAP_M + GAP_HYSTERESIS:
                        if now_ok_to_alert(vid, "DISTANCE_CLEAR", t):
                            write_alert(
                                alert_writer, t, "DISTANCE_CLEAR", vid,
                                f"gap={gap_m:.2f}m >= {MIN_GAP_M + GAP_HYSTERESIS:.2f}m"
                            )
                        brake_active[vid] = False

            # === 3) 超速检测 + 自动限速 ===
            for vid in veh_ids:
                v_ms = traci.vehicle.getSpeed(vid)
                v_kmh = ms_to_kmh(v_ms)
                if v_kmh > SPEED_LIMIT_KMH + OVERSPEED_TOL_KMH:
                    # 将目标速度缓降到限速（或略低）
                    target_ms = kmh_to_ms(SPEED_LIMIT_KMH)
                    traci.vehicle.slowDown(vid, target_ms, int(SLOWDOWN_DURATION_S * 1000))
                    if now_ok_to_alert(vid, "OVERSPEED", t):
                        write_alert(
                            alert_writer, t, "OVERSPEED", vid,
                            f"speed={v_kmh:.1f}km/h > limit={SPEED_LIMIT_KMH:.1f}km/h"
                        )

    traci.close()
    print(f"✅ Wrote {OUT_CSV} (via TraCI)")
    print(f"✅ Wrote {ALERTS_CSV} (events)")

if __name__ == "__main__":
    # 基本的存在性检查（可选）
    if not Path(SUMO_BIN).exists():
        raise SystemExit(f"SUMO binary not found at: {SUMO_BIN}")
    # cfg/net/routes 至少有一个存在
    if not Path("sumo.sumocfg").exists() and not (Path("road.net.xml").exists() and Path("routes.rou.xml").exists()):
        raise SystemExit("Missing sumo.sumocfg or (road.net.xml + routes.rou.xml)")
    main()
