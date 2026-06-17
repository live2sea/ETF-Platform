# Trade Auto-Import Design

**Date**: 2026-06-17
**Status**: Approved

## Problem

每次从同花顺客户端导出 Excel 后，需要手动运行 trade_import.py 导入到 SQLite。流程打断感强，希望实现拖拽即导入。

## Scope

- 交易 Excel 文件的自动导入
- 合并去重逻辑（增量写入，不删历史）
- 不改变现有 TradeImporter 的核心职责

## Design

### 用户操作流

同花顺导出 Excel → 拖入 data/import/ → 自动完成导入

### 去重策略

组合键：(trade_date, trade_time, etf_code, trade_type, price, quantity)

同一天同一时间同一 ETF 同一方向同一价格同一数量 = 同一条记录，跳过。

### 目录结构

data/import/         ← 投递口
data/import/archive/ ← 已导入文件归档

### 代码改动

| 文件 | 动作 | 说明 |
|---|---|---|
| ods/trade_import.py | 修改 | save_sqlite 改为增量 INSERT，增加去重 |
| tools/trade_watcher.py | 新建 | 批量扫描导入 + 归档 |
| run_daily.py | 修改 | 流水线开头先处理积压文件 |

### trade_import.py 改动

save_sqlite 改为：
1. 读 ods_trade_record 已有记录 → 构造去重键 set
2. 新 DataFrame 逐行过滤出新记录
3. INSERT 新记录（不再 DELETE）
4. 打印「导入 N 条新记录，跳过 M 条重复」

### trade_watcher.py 职责

1. 扫描 data/import/*.xlsx，逐个调用 TradeImporter().run()
2. 导入成功后移到 archive/
3. 失败的文件留原地并打印错误

### run_daily.py 改动

在现有 job 列表之前新增批量导入段。

## Non-Goals

- 不做实时 watchdog 常驻进程
- 不做网页端上传
- 不做交易记录编辑/覆盖

## Testing

tests/test_trade_watcher.py：
- 构造含 3 新 + 2 重复的 Excel，第一次导入 → 3 条写入
- 第二次导入同一文件 → 0 条写入
- 构造增量 Excel → 只写新增

## Dependencies

watchdog 6.0.0 / openpyxl 3.1.5 / pandas 2.3.0（均已安装）
