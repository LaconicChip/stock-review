# 股票复盘系统（stock-review）

每个交易日收盘后自动完成 A 股复盘：**大盘全景 + 自选股行情 + 板块资金流 + 科技新闻 + 买卖建议**，一份数据产出两种形态（本地网页 + 单文件 HTML 报告）。

> 这是我的个人复盘工具，开源出来供参考。**不含任何个人持仓、自选股与复盘数据**——数据层完全本地化，见下方「数据与隐私」。

## 功能一览

- **大盘全景**：指数行情、涨跌统计、涨跌停分布、两融/估值/风格轮动等 7 个模块
- **自选股跟踪**：从腾讯自选股 App 实时同步清单，逐股行情 + 新闻/公告
- **板块与资金**：行业/概念板块涨跌排名、主力资金净流入/流出 Top N
- **科技新闻**：每日抓取产品发布、融资、技术突破、行业标准四类热点
- **买卖建议**：基于量化评分（七维评分 + 多周期概率）与当日新闻生成，仅供参考
- **双产物**：Vue 3 本地网页（可翻历史）+ 单文件 HTML 报告（微信直接发）

## 怎么用

| 你要干什么 | 怎么做 |
|---|---|
| 启动本地网页服务 | `bash scripts/start_web.sh`（默认端口 8787，后台守护） |
| 停止本地网页服务 | `bash scripts/start_web.sh stop` |
| 查看运行状态 | `bash scripts/start_web.sh status` |
| 重启服务 | `bash scripts/start_web.sh restart` |
| 浏览器打开 | `http://localhost:8787/web/index.html` |
| 生成某天报告 | `python scripts/build_report.py YYYY-MM-DD` |
| 校验某天数据 | `python tests/validate_data.py data/daily/YYYY-MM-DD.json` |
| 改自选股 | 在腾讯自选股 App 里增删，复盘时自动同步；本地兜底清单从 `config/stocks.example.json` 复制为 `config/stocks.json` |

> 服务脚本支持 `start | stop | restart | status` 四个子命令，无参数默认 `start`。
> PID 写在 `.stock-review.pid`，日志在 `.stock-review.log`（均已被 gitignore）。

## 自动复盘（每日定时）

由 WorkBuddy 自动化任务承担：**每个交易日 20:30** 自动拉数据 → 量化评分 → 搜新闻 → 写 JSON → 校验 → 生成报告。非交易日自动跳过。

## 核心目录

```
stock-review/
  config/      复盘参数 + 自选股清单模板（真实清单本地保留）
  data/        每日复盘数据（个人记录，不进版本库）
    daily/       每天一个文件：YYYY-MM-DD.json
    index.json   日期索引，网页靠它列历史
  web/         本地网页（Vue 3，CDN 依赖已本地化，无构建步骤）
  templates/   HTML 报告模板
  outputs/     生成的每日报告（不进版本库）
  scripts/     启停脚本 + 报告构建 + 历史补做
  tests/       数据契约校验
  docs/        架构图、文件地图、数据契约（v6）
```

## 数据与隐私

本仓库**只包含代码、模板与文档**，以下个人数据均不进版本库（`.gitignore` 已隔离）：

- `data/` 下的每日复盘 JSON 与索引
- `outputs/` 下的报告产物
- `config/stocks.json` 真实自选股清单
- 每日原始抓取数据与临时脚本归档

克隆后按 `docs/data_contract.md` 的契约自行产出数据即可运行。

## 数据来源

- 行情/板块/资金流/新闻：腾讯自选股连接器（westock-mcp），需在 WorkBuddy 连接器管理页授权一次
- 量化评分：stock-researcher 七维评分模型（纯 Python 标准库实现）

## 明确不做

- 登录/账号体系
- 移动端适配
- 上云部署
- 交易记录复盘

## 免责声明

本项目所有产出（含买卖建议、量化评分）仅为个人学习与记录用途，**不构成任何投资建议**。市场有风险，投资需谨慎。
