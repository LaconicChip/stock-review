#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_data.py — 对照 docs/data_contract.md 校验当日复盘 JSON。

用法：
  python3 tests/validate_data.py                # 校验 data/daily/ 下最新一份
  python3 tests/validate_data.py <文件路径>      # 校验指定文件

规则与 docs/data_contract.md 保持一致。任一校验失败退出码为 1，并打印缺失字段路径。
仅用 Python 标准库。
"""
import json
import os
import sys
import glob

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAILY_DIR = os.path.join(PROJECT_ROOT, "data", "daily")


def err(errors, path, msg):
    errors.append(f"  [FAIL] {path}: {msg}")


def is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def validate(obj, fname_date=None):
    errors = []

    # ---- meta ----
    meta = obj.get("meta")
    if not isinstance(meta, dict):
        err(errors, "meta", "应为 object")
    else:
        for f in ("date", "generated_at", "source"):
            if not isinstance(meta.get(f), str) or meta.get(f) == "":
                err(errors, f"meta.{f}", "必填且为非空 string")
        if fname_date and meta.get("date") != fname_date:
            err(errors, "meta.date", f"应等于文件名日期 {fname_date}，实为 {meta.get('date')}")

    # ---- market ----
    market = obj.get("market")
    if not isinstance(market, dict):
        err(errors, "market", "应为 object")
    else:
        # overview
        ov = market.get("overview")
        if not isinstance(ov, list) or len(ov) == 0:
            err(errors, "market.overview", "应为非空 array")
        else:
            for i, item in enumerate(ov):
                p = f"market.overview[{i}]"
                for f in ("type", "desc", "group", "date"):
                    if not isinstance(item.get(f), str):
                        err(errors, f"{p}.{f}", "必填 string")
                metrics = item.get("metrics")
                if not isinstance(metrics, list) or len(metrics) == 0:
                    err(errors, f"{p}.metrics", "应为非空 array")
                else:
                    for j, m in enumerate(metrics):
                        mp = f"{p}.metrics[{j}]"
                        for f in ("key", "label"):
                            if not isinstance(m.get(f), str):
                                err(errors, f"{mp}.{f}", "必填 string")
                        if not isinstance(m.get("value"), (str, int, float)) or isinstance(m.get("value"), bool):
                            err(errors, f"{mp}.value", "应为 string 或 number")

        # breadth
        br = market.get("breadth")
        if not isinstance(br, dict):
            err(errors, "market.breadth", "应为 object")
        else:
            for f in ("upCount", "downCount", "flatCount", "upLimitCount",
                      "downLimitCount", "upRatio"):
                if not is_number(br.get(f)):
                    err(errors, f"market.breadth.{f}", "必填 number")
            # suspensionCount 允许 null（历史补做日 data_changedist 已滚动，无法回溯）
            sc = br.get("suspensionCount")
            if sc is not None and not is_number(sc):
                err(errors, "market.breadth.suspensionCount", "应为 number 或 null")
            # detail 允许空数组（历史补做日无精细分布）
            if not isinstance(br.get("detail"), list):
                err(errors, "market.breadth.detail", "应为 array")

        # sectors
        sec = market.get("sectors")
        if not isinstance(sec, dict):
            err(errors, "market.sectors", "应为 object")
        else:
            for key in ("leading_plates", "lagging_plates", "leading_concepts", "lagging_concepts"):
                arr = sec.get(key)
                if not isinstance(arr, list):
                    err(errors, f"market.sectors.{key}", "应为 array")
                else:
                    for j, it in enumerate(arr):
                        ip = f"market.sectors.{key}[{j}]"
                        if not isinstance(it.get("name"), str):
                            err(errors, f"{ip}.name", "必填 string")
                        if not is_number(it.get("zdf")):
                            err(errors, f"{ip}.zdf", "必填 number")
                        if not is_number(it.get("main_inflow")):
                            err(errors, f"{ip}.main_inflow", "必填 number")

        # overview 必含子模块（前端隐藏但数据必产）
        if isinstance(ov, list):
            types = {item.get("type") for item in ov if isinstance(item, dict)}
            for req in ("technical", "valuation", "rotation"):
                if req not in types:
                    err(errors, "market.overview", f"缺少必产子模块 type={req}")

        # new_highs
        nh = market.get("new_highs")
        if not isinstance(nh, dict):
            err(errors, "market.new_highs", "应为 object")
        else:
            if not is_number(nh.get("count")):
                err(errors, "market.new_highs.count", "必填 number")
            for f in ("window", "as_of", "note"):
                if not isinstance(nh.get(f), str) or nh.get(f) == "":
                    err(errors, f"market.new_highs.{f}", "必填非空 string")

        # clusters
        cl = market.get("clusters")
        if not isinstance(cl, list) or len(cl) == 0:
            err(errors, "market.clusters", "应为非空 array")
        else:
            for i, c in enumerate(cl):
                cp = f"market.clusters[{i}]"
                if not isinstance(c.get("name"), str):
                    err(errors, f"{cp}.name", "必填 string")
                members = c.get("members")
                if not isinstance(members, list) or len(members) == 0:
                    err(errors, f"{cp}.members", "应为非空 array")
                else:
                    for j, m in enumerate(members):
                        mp = f"{cp}.members[{j}]"
                        if not isinstance(m.get("name"), str):
                            err(errors, f"{mp}.name", "必填 string")
                        if not is_number(m.get("zdf")):
                            err(errors, f"{mp}.zdf", "必填 number")
                        if not is_number(m.get("zljlr_yi")):
                            err(errors, f"{mp}.zljlr_yi", "必填 number")
                        if not isinstance(m.get("lead_stock"), str):
                            err(errors, f"{mp}.lead_stock", "必填 string")
                        if not is_number(m.get("lead_zdf")):
                            err(errors, f"{mp}.lead_zdf", "必填 number")

        # conclusion
        if not isinstance(market.get("conclusion"), str):
            err(errors, "market.conclusion", "必填 string")

    # ---- watchlist ----
    wl = obj.get("watchlist")
    if not isinstance(wl, list):
        err(errors, "watchlist", "应为 array")
    else:
        for i, st in enumerate(wl):
            p = f"watchlist[{i}]"
            if not isinstance(st.get("code"), str) or not isinstance(st.get("name"), str):
                err(errors, f"{p}.code/name", "必填 string")
            q = st.get("quote")
            if not isinstance(q, dict):
                err(errors, f"{p}.quote", "应为 object")
            else:
                for f in ("price", "change_percent"):
                    if not is_number(q.get(f)):
                        err(errors, f"{p}.quote.{f}", "必填 number")
            for f in ("news", "notice"):
                if not isinstance(st.get(f), list):
                    err(errors, f"{p}.{f}", "应为 array")

    return errors


def latest_daily():
    files = sorted(glob.glob(os.path.join(DAILY_DIR, "*.json")))
    if not files:
        return None
    return files[-1]


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = latest_daily()
        if not path:
            print("未找到 data/daily/ 下任何 JSON 文件。")
            sys.exit(1)
        print(f"未指定文件，自动校验最新一份：{os.path.basename(path)}")

    fname = os.path.basename(path)
    fname_date = None
    if fname.endswith(".json"):
        fname_date = fname[:-5]

    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
    except Exception as e:
        print(f"读取/解析失败：{e}")
        sys.exit(1)

    errors = validate(obj, fname_date)
    if errors:
        print(f"校验失败（{len(errors)} 处问题）：")
        print("\n".join(errors))
        sys.exit(1)
    else:
        print(f"✅ 校验通过：{fname}")
        sys.exit(0)


if __name__ == "__main__":
    main()
