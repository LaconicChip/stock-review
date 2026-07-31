# 股票复盘系统

每个交易日收盘后自动完成复盘：大盘全景 + 自选股，一份数据双产物（网页 + 单文件报告）。

## 它产出什么（双产物）

1. **本地网页** —— 纯静态 Vue 3 页面，打开 localhost 能看当日复盘、翻历史
2. **单文件 HTML 报告** —— 存在 `outputs/`，微信直接发给朋友就能看

## 怎么用

| 你要干什么 | 怎么做 |
|---|---|
| 启动本地网页服务 | `bash scripts/start_web.sh`（默认端口 8787，后台守护） |
| 停止本地网页服务 | `bash scripts/start_web.sh stop` |
| 查看运行状态 | `bash scripts/start_web.sh status` |
| 重启服务 | `bash scripts/start_web.sh restart` |
| 浏览器打开 | `http://localhost:8787/web/index.html` |
| 发报告给朋友 | 从 `outputs/` 取当天的 HTML 文件，微信发出去 |
| 改自选股 | 在腾讯自选股 App 里增删即可，次日 20:30 复盘自动同步；本地兜底清单见 `config/stocks.json`（gitignore，首次从 `config/stocks.example.json` 复制） |
| 手动触发一次复盘 | 在 WorkBuddy 里说"跑一次复盘" |

> 服务脚本支持 `start | stop | restart | status` 四个子命令，无参数默认 `start`。
> PID 写在 `.stock-review.pid`，日志在 `.stock-review.log`（均已被 gitignore）。

## 自动复盘（每日定时）

由 WorkBuddy 自动化任务承担：**每个交易日 20:30** 自动拉数据 → 写 JSON → 校验 → 生成报告。
非交易日（周末/法定节假日）会自动跳过。触发时间可在 WorkBuddy 自动化设置里改。

## 核心目录

```
stock-review/
  config/      自选股清单、复盘参数
  data/        每日复盘数据（JSON，历史档案，进版本库）
    daily/       每天一个文件：YYYY-MM-DD.json
    index.json   日期索引，网页靠它列历史
  web/         本地网页（Vue 3，无构建，直接打开即用）
  templates/   HTML 报告模板
  outputs/     生成的每日报告（不进版本库）
  scripts/     启动/停止脚本 + 报告构建
  tests/       数据契约校验
  docs/        架构图、文件地图、数据契约、交接卡
  archive/     临时文件/日志/旧备份（见 archive/README.md）
```

## 明确不做

- 登录/账号体系
- 移动端适配
- 上云部署
- 交易记录复盘

## 数据来源

腾讯自选股连接器（westock-mcp）。需在 WorkBuddy 连接器管理页授权一次。
