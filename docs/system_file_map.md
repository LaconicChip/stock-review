# 系统文件地图

> 新增文件后必须更新本图。接手任务先按分类选最小文件集，不扫全项目。
> 状态：✅ 已存在｜📝 已规划未创建

## 核心运行链路

| 文件 | 作用 | 状态 |
|---|---|---|
| AGENTS.md | AI 接手规则，每日复盘执行流程 | ✅ |
| docs/architecture.md | 流程图与模块设计 | ✅ |
| docs/data_contract.md | 数据契约（字段以连接器实测为准，已定稿 v4） | ✅ |
| config/settings.json | 复盘参数（异动阈值等） | ✅ |

## 数据源

| 文件 | 作用 | 状态 |
|---|---|---|
| config/stocks.json | 自选股清单（真实文件 gitignore，仓库仅留 stocks.example.json） | ✅ |
| 腾讯自选股连接器 | 行情/板块/资金流/新闻（外部依赖） | ✅（已授权连接） |

## 业务逻辑

本项目无独立业务代码：复盘判断 = AI 按 settings.json 阈值 + 架构文档规则执行。

## 展示 / UI

| 文件 | 作用 | 状态 |
|---|---|---|
| web/index.html | 本地网页入口（Vue 3，读 data/，样式内联无需 assets） | ✅ |
| templates/report.html | 单文件报告模板（含 `__REVIEW_DATA__` 占位） | ✅ |
| outputs/2026-07-29.html | 每日报告产物（已生成示例） | ✅ |

## 测试

| 文件 | 作用 | 状态 |
|---|---|---|
| tests/validate_data.py | 对照契约校验当日 JSON | ✅ |
| archive/temp/sample_2026-07-29.json | 连接器真实返回样例（契约定稿依据） | ✅ |

## 实验

（暂无。试验性页面/样式统一放 archive/design_previews/，不进 web/）

## 调度

| 位置 | 作用 | 状态 |
|---|---|---|
| WorkBuddy 自动化任务 | 交易日 20:30 触发复盘（Recurring 周一~周五，已创建） | ✅ |
| scripts/start_web.sh | 本地网页服务快速启停控制器（start/stop/restart/status，http.server 后台守护 + pidfile） | ✅ |
| scripts/build_report.py | 把当日 JSON 嵌入模板生成 outputs/报告 | ✅ |
| scripts/backfill_daily.py | 历史补做日通用构建脚本（K线行情 + overview + fund → 组装当日 JSON；用法见文件头） | ✅ |

## 归档

| 目录 | 内容 |
|---|---|
| archive/design_previews/ | 页面设计预览 |
| archive/debug_logs/ | 排错日志 |
| archive/temp/ | 临时文件（接口样例等） |
| archive/backups/ | 旧版本备份 |
