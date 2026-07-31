# AGENTS.md — AI 接手本项目前必读

## 接手顺序（每次必读）

1. 本文件
2. `docs/current_task_handoff.md` —— 当前目标、已确认结论、未解决问题
3. `docs/system_file_map.md` —— 按它选最小文件集，**不要默认扫全项目**

## 最高行为准则

用户全局规则 `~/claude.md`（先想后写、简单优先、外科手术式修改、目标驱动、八荣八耻）对本项目完全适用，优先级高于本文件其余内容。要点复述：

- 调接口前先查文档/代码确认签名，不瞎猜
- 需求不明先确认，业务决策用户拍板
- 复用现有，不造轮子
- 写完必须实际运行验证
- 不懂直说，不装懂

## 本项目特有规则

1. **文件行数红线**：>500 行提示风险；>1000 行必须提拆分方案；>2000 行禁止加新功能，先拆
2. **文档同步**：长任务前后更新 `docs/current_task_handoff.md`；新增文件后更新 `docs/system_file_map.md`
3. **归档纪律**：临时文件、日志、设计预览、旧备份立刻进 `archive/` 对应子目录，不堆根目录
4. **数据契约神圣**：`data/daily/*.json` 的字段结构以 `docs/data_contract.md` 为准；写数据前必读，改契约必须用户确认
5. **上下文刹车**：估算用量接近 60% 先更新交接卡；超 70% 或明显变慢，总结状态并建议用户开新窗口

## 技术边界（已拍板，不要擅自改）

- 无后端、无数据库：数据层 = `data/` 下的 JSON 文件
- 网页 = 纯静态 Vue 3（CDN 引入，无构建步骤），只读 `data/` 的 JSON
- 数据采集 = WorkBuddy 定时任务驱动 AI，经腾讯自选股连接器拉取
- 数据源字段以连接器实际返回为准，**先在 archive/temp/ 里存样例再定契约**

## 每日复盘的执行流程（自动化任务的干活顺序）

1. 读 `config/stocks.json`（自选股）和 `config/settings.json`（参数）
2. 经连接器拉：大盘指数/涨跌统计/板块/资金流向 + 各自选股行情、新闻公告
3. 按 `docs/data_contract.md` 写 `data/daily/YYYY-MM-DD.json`，并更新 `data/index.json`
4. 按 `templates/report.html` 渲染当天报告到 `outputs/YYYY-MM-DD.html`
5. 用 `tests/validate_data.py` 校验当天 JSON，通过才算完成
6. 更新交接卡"今日复盘记录"一节
