#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_report.py — 把当日 JSON 嵌入模板，生成单文件 HTML 报告。

用法：
  python3 scripts/build_report.py                  # 生成 data/daily/ 下最新一份的报告
  python3 scripts/build_report.py 2026-07-29      # 生成指定日期
  python3 scripts/build_report.py 2026-07-29 --open  # 生成并尝试打开

输出：outputs/YYYY-MM-DD.html（双击即可看，可直接发微信）。
"""
import json
import os
import sys
import glob
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(PROJECT_ROOT, "templates", "report.html")
DAILY_DIR = os.path.join(PROJECT_ROOT, "data", "daily")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs")


def latest_daily():
    files = sorted(glob.glob(os.path.join(DAILY_DIR, "*.json")))
    return os.path.basename(files[-1])[:-5] if files else None


def main():
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        date = sys.argv[1]
    else:
        date = latest_daily()
        if not date:
            print("未找到 data/daily/ 下任何 JSON。")
            sys.exit(1)

    daily_path = os.path.join(DAILY_DIR, f"{date}.json")
    if not os.path.exists(daily_path):
        print(f"不存在：{daily_path}")
        sys.exit(1)

    with open(TEMPLATE, "r", encoding="utf-8") as f:
        tpl = f.read()
    with open(daily_path, "r", encoding="utf-8") as f:
        daily_json = f.read()

    if "__REVIEW_DATA__" not in tpl:
        print("模板缺少 __REVIEW_DATA__ 占位符。")
        sys.exit(1)

    out = tpl.replace("__REVIEW_DATA__", daily_json)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{date}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"✅ 已生成：{out_path}")

    if "--open" in sys.argv:
        try:
            subprocess.run(["open", out_path])
        except Exception as e:
            print(f"打开失败：{e}")


if __name__ == "__main__":
    main()
