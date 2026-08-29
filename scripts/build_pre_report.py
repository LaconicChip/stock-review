#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_pre_report.py — 把盘前 JSON 嵌入模板，生成单文件盘前速览 HTML 报告。

用法：
  python3 scripts/build_pre_report.py 2026-08-31            # 生成指定日期
  python3 scripts/build_pre_report.py                       # 生成 data/pre/ 下最新一份

输入：data/pre/YYYY-MM-DD.json（结构 { meta, market: { pre } }，见契约 v7）
输出：outputs/pre/YYYY-MM-DD-pre.html（单文件，可直接推送/分享）。
"""
import json
import os
import sys
import glob

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(PROJECT_ROOT, "templates", "pre_report.html")
PRE_DIR = os.path.join(PROJECT_ROOT, "data", "pre")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "pre")


def latest_pre():
    files = sorted(glob.glob(os.path.join(PRE_DIR, "*.json")))
    return os.path.basename(files[-1])[:-5] if files else None


def main():
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        date = sys.argv[1]
    else:
        date = latest_pre()
        if not date:
            print("未找到 data/pre/ 下任何 JSON。")
            sys.exit(1)

    pre_path = os.path.join(PRE_DIR, f"{date}.json")
    if not os.path.exists(pre_path):
        print(f"不存在：{pre_path}")
        sys.exit(1)

    with open(TEMPLATE, "r", encoding="utf-8") as f:
        tpl = f.read()
    with open(pre_path, "r", encoding="utf-8") as f:
        pre_json = f.read()

    if "__PRE_DATA__" not in tpl:
        print("模板缺少 __PRE_DATA__ 占位符。")
        sys.exit(1)

    out = tpl.replace("__PRE_DATA__", pre_json)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{date}-pre.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"✅ 已生成：{out_path}")


if __name__ == "__main__":
    main()
