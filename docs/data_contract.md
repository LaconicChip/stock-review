# 数据契约 data_contract.md

> 每日复盘产出文件：`data/daily/YYYY-MM-DD.json`
> 本契约由 `archive/temp/sample_2026-07-29.json`（真实连接器返回）定稿。
> **写数据前必读；改契约必须用户确认。** 网页、报告、校验脚本三方都按此读取。

## 顶层结构

```json
{
  "meta":   { ... },   // 元信息（必填）
  "market": { ... },   // 大盘全景（必填）
  "watchlist": [ ... ] // 自选股复盘（必填，可为空数组）
}
```

## meta（必填，object）

| 字段 | 类型 | 必填 | 说明 |
|---|---|:---:|---|
| date | string | ✅ | 交易日，`YYYY-MM-DD`，须与文件名日期一致 |
| generated_at | string | ✅ | 生成时间，ISO 8601，如 `2026-07-30T02:00:00` |
| source | string | ✅ | 数据来源，固定 `"westock-mcp"` |
| note | string | - | 备注，如异常说明 |

## market（必填，object）

### market.overview（必填，array，非空）
市场总览，由 `data_market_overview(type=all)` 的 8 个子模块**拍平**而来。
原始返回每个子模块含 `row`（数值）+ `schema`（中文标签），写入时合并为 `metrics` 列表，页面/报告直接渲染，无需再查 schema。

```json
{
  "type": "summary",          // 子模块类型：summary|trade|interval|technical|updown|margin|valuation|rotation
  "desc": "市场画像总评",       // 中文描述
  "group": "综合",             // 分组
  "date": "2026-07-29",
  "metrics": [                // 指标列表（非空）
    { "key": "ADJ_SCORE", "label": "调整评分", "value": 18.44 },
    { "key": "SENTIMENT_STATUS", "label": "情绪指标状态", "value": "情绪狂热(...)" }
  ]
}
```
- `value` 类型混合（number 或 string），按原始值存放；校验只查存在性与类型 ∈ {number, string}。

### market.breadth（必填，object）—— 涨跌分布，来自 `data_changedist`
| 字段 | 类型 | 必填 |
|---|---|:---:|
| upCount / downCount / flatCount | number | ✅ |
| upLimitCount / downLimitCount | number | ✅ |
| suspensionCount | number \| null | ✅ | 停牌家数；**历史补做日** `data_changedist` 已滚动到当日、无法回溯时可置 `null` |
| upRatio | number | ✅ |
| comment | string | ✅ |
| totalAmount | number | ✅ | 成交额（元） |
| amountChange | number | ✅ |
| detail | array | ✅ | 可为**空数组** `[]`（含 11 档：`[{ "section": "涨停", "count": 86, "flag": 1 }]`，flag: 1涨 / -1跌 / 0平）；**历史补做日** `data_changedist` 已滚动、精细分档不可回溯时置 `[]`（前端显示「该交易日为历史补做日，精细涨跌分档数据已不可回溯」） |

### market.sectors（必填，object）—— 板块轮动，来自 `data_sector(mode=ranking)` 的 `fundflow` 部分**截取**
只保留资金流（主力净流入 `zljlr`，单位万元）领先/落后各 top3，丢弃庞大的 `rank` 榜单数组。
| 字段 | 类型 | 说明 |
|---|---|---|
| leading_plates | array | 资金流入领先行业 top3 |
| lagging_plates | array | 资金流入落后行业 top3 |
| leading_concepts | array | 资金流入领先概念 top3 |
| lagging_concepts | array | 资金流入落后概念 top3 |

每项结构：
```json
{ "code": "pt01801764", "name": "游戏Ⅱ", "zdf": 5.43, "main_inflow": 161037.08, "lead_stock": { "name": "电魂网络", "zdf": "10.03" } }
```
- `main_inflow` = 原始 `zljlr`（主力净流入，万元）；`lead_stock` = 原始 `lzg`（领涨股）。

### market.new_highs（必填，object）—— 百日新高
来自 `data_market_overview(type=updown)` 的 `CNT_HIGH120`（创120日新高家数）。
⚠️ 连接器**无精确100日口径**，仅提供 5/10/20/60/120/250 日；且**不提供个股列表**，前端只展示家数 + 口径说明。
| 字段 | 类型 | 必填 | 说明 |
|---|---|:---:|---|
| count | number | ✅ | 创 `window` 新高家数 |
| window | string | ✅ | 窗口说明，如 `"120日"` |
| as_of | string | ✅ | 对应交易日 `YYYY-MM-DD` |
| note | string | ✅ | 口径/限制说明 |

### market.clusters（必填，array）—— 集群详情导航
板块按主题聚类（如科技硬件/消费/医药/金融/情绪交易/价值政策），**数据来自 `data_sector(mode=ranking)` 资金流 top/bottom 各3**，由 AI 按板块名称归并到主题，前端点击展开看领涨股与资金。
```json
{
  "name": "科技硬件集群",
  "members": [
    { "name": "半导体", "zdf": 5.97, "zljlr_yi": 135.14, "lead_stock": "杰华特", "lead_zdf": 20.0 }
  ]
}
```
| 字段 | 类型 | 必填 | 说明 |
|---|---|:---:|---|
| name | string | ✅ | 集群名（主题） |
| members[].name | string | ✅ | 板块名 |
| members[].zdf | number | ✅ | 板块涨跌幅(%) |
| members[].zljlr_yi | number | ✅ | 主力净流入（亿元，原始 zljlr 万元 ÷ 1e4） |
| members[].lead_stock | string | ✅ | 领涨股名 |
| members[].lead_zdf | number | ✅ | 领涨股涨跌幅(%) |

### market.conclusion（必填，string）—— 今日核心结论
AI 基于当日全量数据撰写的中文复盘总结（可含 `\n\n` 分段），前端 `white-space: pre-line` 渲染。

### market.news（可选，object）—— 科技新闻板块（v6 新增，2026-08-17 起每日必产）
AI 搜索当日科技板块热点新闻整理（重点：OpenAI/Google/Anthropic 等公司动态，半导体、电池、锂矿、创新药、电力、光模块、航天等科技领域）。**历史文件可缺失，前端降级隐藏**。
| 字段 | 类型 | 必填 | 说明 |
|---|---|:---:|---|
| date | string | ✅ | 交易日 `YYYY-MM-DD` |
| focus | string | ✅ | 一句话点题（今日科技主线） |
| items | array | ✅ | 新闻条目列表（可为空数组，但补做日建议诚实留空而非编造） |

`items[]` 每项结构（**category 必须为枚举之一**）：
```json
{
  "category": "product",        // 枚举：product 产品/发布 | funding 融资并购 | research 技术突破/论文 | standard 标准规范
  "title": "OpenAI 发布新模型...",
  "summary": "一句话摘要",
  "source": "TechCrunch / 财联社",
  "url": "https://..."          // 可选
}
```
前端按 category 分组渲染四个卡片（产品发布/融资并购/技术突破/标准规范），缺失枚举不渲染对应卡片。

### market.recommendations（可选，object）—— 买入/止盈建议（v6 新增，2026-08-17 起每日必产）
AI 结合当日新闻、大盘形势与自选股表现给出的参考建议。**仅供参考，不构成投资建议。历史文件可缺失，前端降级隐藏。**
| 字段 | 类型 | 必填 | 说明 |
|---|---|:---:|---|
| date | string | ✅ | 交易日 `YYYY-MM-DD` |
| market_analysis | string | ✅ | 国内金融形势分析（流动性/政策/情绪/风险偏好） |
| buy | array | ✅ | 推荐关注/买入列表（可空数组），每项 `{ "name", "code", "reason", "risk" }` |
| take_profit | array | ✅ | 推荐止盈列表（可空数组），每项同上 |
| traditional_note | string | ✅ | 传统行业（如白酒、电力）走势分析 |

`buy[]` / `take_profit[]` 每项：
```json
{ "name": "半导体", "code": "pt01801081", "reason": "资金流+价格共振，突破前高", "risk": "估值高位、情绪过热" }
```

### 前端隐藏字段（数据仍必产）
`market.overview` 中的 `technical`（大盘技术指标）、`valuation`（中证全指估值）、`rotation`（风格指数轮动）**照常分析写入**，每日不遗漏；仅前端 7.29 起不再渲染这三块卡片。契约校验仍要求它们存在于 `overview`。

## watchlist（必填，array）
清单由自动化经 `portfolio_watchlist` 从腾讯自选股 App 实时获取（source=westock；`config/stocks.json` 仅作同步失败兜底）。
**v2（2026-07-30）**：清单支持混合类型，每条必带 `type`；行情分两种口径（见下）。

```json
{
  "code": "sh688825",
  "name": "C长鑫",
  "type": "stock",        // 必填：stock 个股 | index 指数 | plate 板块 | us_index 美股指数
  "quote": { ... },   // 必填，object，字段口径见下
  "news": [ ... ],    // 必填，array，仅 stock 拉取，其余类型固定 []
  "notice": [ ... ]   // 必填，array，仅 stock 拉取，其余类型固定 []
}
```

### watchlist[].quote（必填，object）—— 两种口径

**口径 A：日K（`data_kline` period=day），用于补做/重做历史日数据**
| 字段 | 类型 | 必填 | 说明 |
|---|---|:---:|---|
| price / prev_close / open / high / low | number | ✅ | 收盘/昨收/开/高/低 |
| change / change_percent | number | ✅ | 涨跌额/涨跌幅(%)，由昨收计算 |
| volume / amount | number | ✅ | 成交量/成交额（元） |
| turnover_rate | number \| null | ✅ | 换手率(%)（K线 exchange 字段；美股等无意义置 null） |
| chg_5d / chg_20d / chg_60d / chg_250d / chg_ytd | number \| null | ✅ | 区间涨跌幅(%)，按交易日数；**新股/数据不足置 null，不编造** |
| high_52week / low_52week | number | ✅ | 52周高/低（年窗口内最高/最低；上市不足一年取实际区间） |

**口径 B：实时快照（`data_quote`），仅用于"当日收盘后"生成当天数据**
口径 A 全部字段 + 可选附加：`pe_ratio` / `pb_ratio` / `volume_ratio` / `total_market_cap` / `time`。
⚠️ data_quote 无日期参数，非当日收盘后调用会拿到"今天"的数据，**禁止用于历史日**。

**展示方规则**：quote 中缺失或为 null 的字段一律不渲染对应行（网页/报告共同遵守）。

### watchlist[].news[ ]（必填，array，仅 stock，最多 5 条）
`{ "id": string, "title": string, "time": string, "url": string }`
- 时间过滤：仅保留 `time <= 当日 23:59:59` 的条目（接口只返回最新，补做历史日常被过滤为空数组——这是正常现象，不是错误）。

### watchlist[].notice[ ]（必填，array，仅 stock，最多 5 条）
`{ "id": string, "title": string, "time": string }`（`url` 多为空，省略）；同样按 `time <= 当日` 过滤。

## 校验原则（tests/validate_data.py）
1. 顶层含 `meta` / `market` / `watchlist`，且均为对应类型。
2. `meta.date` 存在且 == 文件名日期；`generated_at` / `source` 存在。
3. `market.overview` 为非空数组；每项含 `type`/`desc`/`group`/`date`/`metrics`（非空，每元素含 `key`/`label`/`value`）。
4. `market.breadth` 含 7 个必填计数字段（number）+ `suspensionCount`（number|null，历史补做日可 null）+ `detail`（array，可为空 `[]`）。
5. `market.sectors` 含 4 个数组（leading/lagging × plates/concepts），每项含 `name`/`zdf`/`main_inflow`。
6. `watchlist` 为数组；每项含 `code`/`name`/`quote`（含 `price`/`change_percent` 为 number）/`news`/`notice`（均为 array）。
7. `market.new_highs` 含 `count`(number)/`window`/`as_of`/`note`（string）；`market.clusters` 为非空数组，每项含 `name` + `members`（非空，元素含 `name`/`zdf`/`zljlr_yi`/`lead_stock`/`lead_zdf`）；`market.conclusion` 为 string。
8. `market.overview` 仍须包含 `technical`/`valuation`/`rotation`（前端隐藏但数据必产）。
9. `market.news`（可选，缺失放行）若存在：含 `date`/`focus`（string）与 `items`（array，元素含 `category`∈{product,funding,research,standard}/`title`/`summary`/`source`，`url` 可选）。
10. `market.recommendations`（可选，缺失放行）若存在：含 `date`/`market_analysis`/`traditional_note`（string）、`buy`/`take_profit`（array，元素含 `name`/`code`/`reason`/`risk` 为 string）。
11. 任一失败则退出码非 0，并打印缺失字段路径。

## 变更记录
- v1（2026-07-29）：初版，watchlist 仅个股、仅实时口径（占位股茅台/宁德）。
- v2（2026-07-30）：watchlist 加 `type`（stock/index/plate/us_index）；quote 分日K/实时两口径，区间与新股字段允许 null；news/notice 限定仅 stock 类型并加时间过滤规则。驱动原因：真实清单同步后含指数/板块/美股指数，且补做历史日必须走日K。
- v3（2026-07-30）：新增 `market.new_highs`（百日新高家数，连接器仅120日口径且无个股列表）、`market.clusters`（板块主题聚类导航，来自资金流排名）、`market.conclusion`（AI 复盘总结）；`technical`/`valuation`/`rotation` 改为前端隐藏但数据仍必产。驱动原因：用户要求前端新增百日新高/集群导航/核心结论三板块，并隐藏大盘技术/估值/风格三块（数据保留）。
- v4（2026-07-30）：放宽 `market.breadth` —— `suspensionCount` 允许 `null`、`detail` 允许空数组 `[]`，仅用于**历史补做日**（`data_changedist` 为实时接口、补做时已滚动到当日，精细分档与停牌家数不可回溯）。当日收盘后正常生成的数据仍应填充真实值。校验脚本与前端同步降级：空 `detail` 不渲染分布条、显示历史补做说明；`suspensionCount` 为 `null` 时显示 `—`。驱动原因：补做 7.30 数据时连接器 `data_changedist` 已返回 7.31，`breadth.detail`/`suspensionCount` 不可回溯。
- v5（2026-07-31）：watchlist[].quote 口径A 新增可选字段 `chg_250d`（number|null，250日涨跌幅%）。A股主板三大指数仍取自 `overview.interval` 的 `CHG_250D_*`，沪深300 取自 `overview.rotation` 的 `CHG_250D_HS300`，美股指数(us_index) 经 `data_kline` 回算。驱动原因：报告"今日指数"卡片含 250日 列，原模板误将 `chg_ytd` 当作 250日 填充（仅 A股三大指数有真实 250日，沪深300/标普500 显示错值或空），现已修正为读取 `chg_250d` 并增加 `null` 置空保护；标普500 经 `data_kline` 回算补入 5/20/60/250日 与 52周 高低。
- v6（2026-08-17）：新增 `market.news`（科技新闻板块：产品发布/融资并购/技术突破/标准规范四枚举分类）与 `market.recommendations`（买入/止盈建议 + 金融形势 + 传统行业分析）。**均为可选字段，历史文件缺失放行**（校验与前端同步降级）；2026-08-17 起每日复盘必产。驱动原因：用户要求复盘总结新增科技热点新闻覆盖（产品发布/融资并购/技术突破/标准规范），并基于新闻+大盘+自选股给出推荐买入/推荐止盈与传统行业分析。
