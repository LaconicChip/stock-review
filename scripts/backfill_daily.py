#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
backfill_daily.py — 历史补做日构建脚本（8.03~8.12）

用法：python backfill_daily.py 2026-08-03 [--prev-money 2540947000000]
输入：
  archive/temp/kline_0803-0812.json   日K（13 标的，覆盖 2026-01-05~08-12）
  archive/temp/{date}_overview.json   data_market_overview(all, date) 扁平 metrics
  archive/temp/{date}_fund.json       data_sector(ranking, date) fundflow top/bottom
  --prev-money                        前一交易日两市成交额（元），用于 amountChange
输出：data/daily/{date}.json
"""
import json, os, sys, datetime

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KLINE = os.path.join(PROJ, "archive", "temp", "kline_main_full.json")
KLINE_SECTOR = os.path.join(PROJ, "archive", "temp", "kline_sector_full.json")

def fnum(x):
    try:
        return float(x)
    except Exception:
        return None

def main():
    target = sys.argv[1]
    prev_money = None
    if "--prev-money" in sys.argv:
        prev_money = float(sys.argv[sys.argv.index("--prev-money") + 1])

    # ---------- 0) 自选股清单（与 App 当前一致，12 项） ----------
    SYMBOLS = [
        ("sh000001", "上证指数", "index"),
        ("sh000300", "沪深300", "index"),
        ("us.IXIC", "纳斯达克", "us_index"),
        ("sh688825", "长鑫科技", "stock"),
        ("pt02051434", "锂矿", "plate"),
        ("pt01801161", "电力", "plate"),
        ("pt02131362", "创新药", "plate"),
        ("sz399997", "中证白酒", "index"),
        ("pt02003574", "锂电池概念", "plate"),
        ("pt01801081", "半导体", "plate"),
        ("pt01801053", "贵金属", "plate"),
        ("pt01801050", "有色金属", "plate"),
    ]

    # ---------- 1) K线 -> watchlist 行情 ----------
    kobj = json.load(open(KLINE, encoding="utf-8"))
    by = {}
    for it in kobj["data"]["data"]:
        by[it["symbol"]] = it["data"]["nodes"]

    def build_quote(sym):
        nodes = by.get(sym)
        if not nodes:
            return None
        idx = next((i for i, n in enumerate(nodes) if n["date"] == target), None)
        if idx is None:
            return None
        today = nodes[idx]
        prev = nodes[idx + 1] if idx + 1 < len(nodes) else None
        price = fnum(today["last"])
        prev_close = fnum(prev["last"]) if prev else None
        change = round(price - prev_close, 4) if (price is not None and prev_close is not None) else None
        change_percent = round(change / prev_close * 100, 2) if change is not None else None

        def chg(nback):
            if idx + nback < len(nodes):
                base = fnum(nodes[idx + nback]["last"])
                if base:
                    return round((price / base - 1) * 100, 2)
            return None
        chg_5d, chg_20d, chg_60d, chg_250d = chg(5), chg(20), chg(60), chg(250)

        chg_ytd = None
        first_2026 = None
        for n in nodes:
            if "2026-01-01" <= n["date"] <= "2026-01-31":
                first_2026 = fnum(n["last"]); break
        if first_2026:
            chg_ytd = round((price / first_2026 - 1) * 100, 2)

        window = nodes[idx: idx + 252] if idx + 252 <= len(nodes) else nodes[idx:]
        hs = [fnum(n["high"]) for n in window if fnum(n["high"]) and fnum(n["high"]) > 0]
        ls = [fnum(n["low"]) for n in window if fnum(n["low"]) and fnum(n["low"]) > 0]
        high_52 = max(hs) if hs else None
        low_52 = min(ls) if ls else None

        exch = today.get("exchange")
        if sym.startswith("us.") or not exch or fnum(exch) == 0:
            turnover_rate = None
        else:
            turnover_rate = fnum(exch)

        return {
            "price": price, "prev_close": prev_close,
            "open": fnum(today["open"]), "high": fnum(today["high"]), "low": fnum(today["low"]),
            "change": change, "change_percent": change_percent,
            "volume": fnum(today["volume"]), "amount": fnum(today["amount"]),
            "turnover_rate": turnover_rate,
            "chg_5d": chg_5d, "chg_20d": chg_20d, "chg_60d": chg_60d,
            "chg_250d": chg_250d, "chg_ytd": chg_ytd,
            "high_52week": high_52, "low_52week": low_52,
        }

    watchlist = []
    for code, name, typ in SYMBOLS:
        q = build_quote(code)
        if q is None:
            print(f"⚠️  跳过（无 {target} K线）：{name}")
            continue
        watchlist.append({"code": code, "name": name, "type": typ, "quote": q, "news": [], "notice": []})

    # ---------- 2) overview（已扁平） ----------
    ymd = f"{target[5:7]}{target[8:10]}"   # 2026-08-03 -> 0803（与归档命名一致）
    ov_path = os.path.join(PROJ, "archive", "temp", f"{ymd}_overview.json")
    if not os.path.exists(ov_path):
        ov_path = os.path.join(PROJ, "archive", "temp", f"{target[2:4]}{target[5:7]}{target[8:10]}_overview.json")
    overview = json.load(open(ov_path, encoding="utf-8"))
    ov_types = {m["type"]: m for m in overview}

    # ---------- 3) breadth：updown+trade 真实值；detail/suspensionCount 降级 ----------
    up = ov_types.get("updown", {})
    tr = ov_types.get("trade", {})
    def metric(mod, key):
        for m in mod.get("metrics", []):
            if m["key"] == key:
                return m["value"]
        return None
    upCount = metric(up, "CNT_RED")
    downCount = metric(up, "CNT_GREEN")
    flatCount = metric(up, "CNT_ZERO")
    upLimit = metric(up, "CNT_REACH_UPLIMIT")
    downLimit = metric(up, "CNT_REACH_DNLIMIT")
    upRatio = metric(up, "RATIO_UP")
    money_yi = metric(tr, "MONEY")
    totalAmount = round(money_yi * 1e8, 2) if money_yi is not None else None
    amountChange = round((money_yi * 1e8) - prev_money, 2) if (money_yi is not None and prev_money) else None

    def ratio_word(r):
        if r is None: return "未知"
        if r >= 70: return "高"
        if r >= 50: return "中等"
        if r >= 30: return "偏低"
        return "低"
    comment = (f"当前市场上涨家数占比全市场{round(upRatio, 2) if upRatio is not None else '—'}%，"
               f"市场情绪{ratio_word(upRatio)}。")

    breadth = {
        "upCount": upCount, "downCount": downCount, "flatCount": flatCount,
        "upLimitCount": upLimit, "downLimitCount": downLimit,
        "suspensionCount": None,
        "upRatio": round(upRatio, 2) if upRatio is not None else None,
        "comment": comment,
        "totalAmount": totalAmount, "amountChange": amountChange,
        "detail": [],
    }

    # ---------- 4) sectors / clusters：fund 文件 ----------
    fund_path = os.path.join(PROJ, "archive", "temp", f"{ymd}_fund.json")
    fund = json.load(open(fund_path, encoding="utf-8"))

    # sectors.zdf 用价格口径（板块日K当日涨跌幅）；clusters.zdf 用资金流口径（fundflow.zdf）
    # 背离日两者不一致（如 8.03 半导体 fundflow +1.87% vs 板块价指 -5.84%），契约明确 sectors=价格、clusters=资金流。
    sec_kline = {}
    try:
        skobj = json.load(open(KLINE_SECTOR, encoding="utf-8"))
        for it in skobj["data"]["data"]:
            nodes = it["data"]["nodes"]
            for i, n in enumerate(nodes):
                if n["date"] == target:
                    prev = nodes[i + 1]["last"] if i + 1 < len(nodes) else None
                    sec_kline[it["symbol"]] = round((fnum(n["last"]) / prev - 1) * 100, 2) if prev else None
                    break
    except Exception as e:
        print(f"⚠️  板块K线读取失败，sectors.zdf 回退 fundflow.zdf：{e}")

    def sec_item(it, price_ok=True):
        zdf = sec_kline.get(it["code"]) if (price_ok and it["code"] in sec_kline) else it["zdf"]
        return {"code": it["code"], "name": it["name"], "zdf": zdf,
                "main_inflow": it["zljlr"], "lead_stock": {"name": it["lzg"], "zdf": str(it["lzg_zdf"])}}

    sectors = {
        "leading_plates": [sec_item(x) for x in fund["plate"]["top"][:3]],
        "lagging_plates": [sec_item(x) for x in fund["plate"]["bottom"][:3]],
        "leading_concepts": [sec_item(x) for x in fund["concept"]["top"][:3]],
        "lagging_concepts": [sec_item(x) for x in fund["concept"]["bottom"][:3]],
    }

    # 集群归并：按主题关键词匹配 12 个板块
    CLUSTER_RULES = [
        ("科技硬件集群", ["半导体", "通信设备", "消费电子", "元件", "TMT", "数据中心", "光模块", "光芯片", "算力"]),
        ("资源·周期集群", ["工业金属", "小金属", "贵金属", "有色金属", "周期股", "煤炭", "钢铁", "石油"]),
        ("消费集群", ["白酒", "食品", "饮料", "家电", "汽车"]),
        ("医药集群", ["医药", "生物", "制药", "CRO", "医疗", "减肥药"]),
        ("金融集群", ["银行", "证券", "保险", "非银"]),
        ("情绪·交易集群", ["连板", "涨停", "高振幅", "高价股", "转融券", "次新"]),
        ("价值·政策集群", ["反内卷", "证金", "破净", "国企", "中特估"]),
    ]
    all_items = fund["plate"]["top"] + fund["plate"]["bottom"] + fund["concept"]["top"] + fund["concept"]["bottom"]
    seen = set()
    clusters = []
    for cname, kws in CLUSTER_RULES:
        members = []
        for it in all_items:
            if it["code"] in seen:
                continue
            if any(kw in it["name"] for kw in kws):
                members.append({"name": it["name"], "zdf": it["zdf"],
                                "zljlr_yi": round(it["zljlr"] / 1e4, 2),
                                "lead_stock": it["lzg"], "lead_zdf": it["lzg_zdf"]})
                seen.add(it["code"])
        if members:
            clusters.append({"name": cname, "members": members})
    # 未归并的兜底进情绪集群（不应发生，防御）
    for it in all_items:
        if it["code"] not in seen:
            clusters.append({"name": "其他", "members": [{"name": it["name"], "zdf": it["zdf"],
                "zljlr_yi": round(it["zljlr"] / 1e4, 2), "lead_stock": it["lzg"], "lead_zdf": it["lzg_zdf"]}]})
            seen.add(it["code"])

    # ---------- 5) new_highs ----------
    cnt_high120 = metric(up, "CNT_HIGH120")
    new_highs = {
        "count": cnt_high120, "window": "120日", "as_of": target,
        "note": "连接器仅提供创120日新高家数（无精确100日口径），且未提供个股列表；数值来自 data_market_overview(type=updown) 的 CNT_HIGH120。",
    }

    # ---------- 6) conclusion（按日期映射，需人工撰写后补充） ----------
    conclusion_map_path = os.path.join(PROJ, "archive", "temp", "conclusions.json")
    if os.path.exists(conclusion_map_path):
        cmap = json.load(open(conclusion_map_path, encoding="utf-8"))
        conclusion = cmap.get(target, "")
    else:
        conclusion = ""

    # ---------- 7) meta ----------
    meta = {
        "date": target,
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "source": "westock-mcp",
        "note": (f"历史补做（{target} 收盘后回补）：overview 各模块来自 data_market_overview(all,{target}) 真实历史数据；"
                 f"breadth 核心（涨/跌/平/涨停/跌停/上涨比/成交额）来自 updown+trade 模块真实值，"
                 f"detail(11档分布)与 suspensionCount 因 data_changedist 为实时接口、无法回取历史，按契约放宽置空；"
                 f"sectors/clusters 来自 data_sector(ranking,{target}) fundflow；"
                 f"new_highs=CNT_HIGH120={cnt_high120}；watchlist 行情经日K({target})计算（自选股清单为回补日当天 App 清单，12 项）。"
                 f"news/notice 接口仅返回最新，历史日按时间过滤后为空，属正常。"),
    }

    doc = {"meta": meta, "market": {"overview": overview, "breadth": breadth,
           "sectors": sectors, "new_highs": new_highs, "clusters": clusters,
           "conclusion": conclusion}, "watchlist": watchlist}

    out = os.path.join(PROJ, "data", "daily", f"{target}.json")
    json.dump(doc, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✅ 已生成 {out}")
    print(f"  overview: {[m['type'] for m in overview]}")
    print(f"  breadth: up={upCount} down={downCount} flat={flatCount} upLimit={upLimit} downLimit={downLimit} ratio={upRatio} amount={totalAmount} chg={amountChange}")
    print(f"  new_highs: {cnt_high120}")
    print(f"  clusters: {[c['name'] for c in clusters]}")
    for w in watchlist:
        q = w["quote"]
        print(f"  {w['name']:<8} 价={q['price']} 涨跌幅={q['change_percent']} 5/20/60/250日={q['chg_5d']}/{q['chg_20d']}/{q['chg_60d']}/{q['chg_250d']} 52周=[{q['low_52week']},{q['high_52week']}]")

if __name__ == "__main__":
    main()
