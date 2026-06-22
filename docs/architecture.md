 # ETF-Platform 系统架构设计文档
 
 ## 一、项目目标
 
 ETF-Platform 是个人 ETF 投资分析平台。
 
 * 自动导入交易记录
 * 自动计算持仓成本与收益
 * 自动计算技术指标（MA、RSI、回撤）
 * 自动拉取宏观数据并生成环境评分
 * 自动生成 ETF 投资信号与调仓建议
 * 自动生成每日复盘报告
 * Dashboard 可视化展示
 
 ---
 
 ## 二、系统全景图
 
 ```mermaid
 graph TB
     subgraph ODS["ODS 原始数据层"]
         direction LR
         O1["trade_import.py<br/>交易记录导入"]
         O2["market_price_loader.py<br/>ETF/LOF 行情加载"]
         O3["market_kline_loader.py<br/>K线数据加载"]
         O4["macro_loader.py<br/>宏观指标加载"]
     end
 
     subgraph POSITION["POSITION 持仓计算层"]
         direction LR
         P1["cost_engine.py<br/>持仓成本计算"]
         P2["profit_engine.py<br/>已实现收益分析"]
         P3["floating_profit_engine.py<br/>浮动盈亏分析"]
         P4["allocation_engine.py<br/>ETF 仓位分析"]
         P5["allocation_category_engine_v2.py<br/>分类仓位分析"]
     end
 
     subgraph FACTOR["FACTOR 技术指标层"]
         direction LR
         FA1["ma_factor_engine.py<br/>均线趋势因子"]
         FA2["rsi_factor_engine.py<br/>RSI 强弱因子"]
         FA3["drawdown_engine.py<br/>回撤风险因子"]
     end
 
     subgraph MACRO["MACRO 宏观分析层<br/>（2026-06 新增）"]
         direction LR
         M1["macro_indicator_engine.py<br/>单指标评分"]
         M2["macro_environment_engine.py<br/>综合环境评分 + 趋势加速度"]
     end
 
     subgraph SIGNAL["SIGNAL 信号生成层"]
         direction LR
         S1["etf_signal_engine.py<br/>ETF 综合信号"]
         S2["signal_trend_engine.py<br/>信号趋势分析"]
     end
 
     subgraph STRATEGY["STRATEGY 策略决策层"]
         direction LR
         ST1["etf_score_engine_v2.py<br/>ETF 综合评分（含宏观风向）"]
         ST2["add_position_engine.py<br/>加仓建议"]
         ST3["rebalance_engine_v2.py<br/>调仓建议"]
         ST4["etf_overlap_engine.py<br/>重仓重叠分析"]
     end
 
     subgraph RISK["RISK 风险控制层"]
         direction LR
         R1["risk_engine.py<br/>风险分析（含宏观仓位上限）"]
         R2["position_health_engine.py<br/>持仓健康度"]
     end
 
     subgraph DASHBOARD["DASHBOARD 可视化展示层<br/>home.py 多视图"]
         direction LR
         DA1["🏠 总览<br/>宏观环境 + 资产概览"]
         DA2["📊 持仓明细<br/>成本/盈亏/仓位"]
         DA3["⭐ ETF 评分<br/>评分排行 + 宏观风向分"]
         DA4["⚠️ 风险分析<br/>仓位上限 + 超限预警"]
         DA5["📝 每日复盘<br/>当日回顾"]
         DA6["🗃️ 数据状态<br/>各表数据概览"]
         DA7["🧠 投资决策中心<br/>AI 决策辅助"]
     end
 
     ODS --> POSITION
     ODS --> FACTOR
     ODS --> MACRO
     POSITION --> SIGNAL
     FACTOR --> SIGNAL
     MACRO --> STRATEGY
     MACRO --> RISK
     SIGNAL --> STRATEGY
     POSITION --> STRATEGY
     POSITION --> RISK
     STRATEGY --> RISK
     STRATEGY --> DASHBOARD
     RISK --> DASHBOARD
     POSITION --> DASHBOARD
     MACRO --> DASHBOARD
     MACRO --> SIGNAL
 ```
 
 ---
 
 ## 三、模块与数据表说明
 
 ### ODS 层 — 原始数据采集
 
 从外部数据源拉取数据，写入 ODS 表。**不继承 BaseEngine**，直接使用 akshare + pandas + sqlite3。
 
 | 模块文件 | 数据源 | 输出表 | 表中文名 | 业务含义 | 更新频率 |
 |---|---|---|---|---|---|
 | `ods/trade_import.py` | 同花顺导出 Excel | `ods_trade_record` | 交易记录表 | 用户的每笔 ETF 买卖记录：日期、代码、方向、价格、数量 | 不定期（拖入 Excel 触发） |
 | `ods/market_price_loader.py` | AKShare | `ods_market_price` | 行情快照表 | 持仓 ETF 的最新价格，用于计算浮动盈亏 | 每日 |
 | `ods/market_kline_loader.py` | AKShare | `ods_market_kline` | K线历史表 | 每只 ETF 的日线 OHLCV 数据，技术指标计算的基础 | 每日 |
 | `ods/macro_loader.py` | AKShare | `ods_macro_indicator` | 宏观指标原始表 | 8 个核心宏观指标（PMI、M2、CPI、PPI、中美利差、美联储利率、沪深300 PE、北向资金）的原始值 | 每日 |
 
 ---
 
 ### POSITION 层 — 持仓计算
 
 基于交易记录和行情，计算持仓成本、收益、仓位分布。
 
 | 模块文件 | 输入表 | 输出表 | 表中文名 | 业务含义 |
 |---|---|---|---|---|
 | `engine/position/cost_engine.py` | `ods_trade_record` | `dwd_position` | 持仓明细表 | 每只 ETF 的当前持仓数量、持仓成本、持仓市值 |
 | `engine/position/profit_engine.py` | `ods_trade_record` | `dwd_profit_analysis` | 已实现收益表 | 已完成交易的盈亏金额和收益率 |
 | `engine/position/floating_profit_engine.py` | `dwd_position` + `ods_market_price` | `dwd_floating_profit` | 浮动盈亏表 | 每只 ETF 的未实现盈亏（浮盈/浮亏金额及百分比） |
 | `engine/position/allocation_engine.py` | `dwd_floating_profit` | `dwd_allocation` | 仓位分配表 | 每只 ETF 占总仓位的百分比 |
 | `engine/position/allocation_category_engine_v2.py` | `dwd_allocation` | `dwd_category_allocation` | 分类仓位表 | 按类别（港股科技、美股科技、红利等）汇总的仓位占比 |
 
 ---
 
 ### FACTOR 层 — 技术指标计算
 
 基于 K 线数据，计算技术分析因子，输出评分和信号。
 
 | 模块文件 | 输入表 | 输出表 | 表中文名 | 业务含义 |
 |---|---|---|---|---|
 | `engine/factor/ma_factor_engine.py` | `ods_market_kline` | `dwd_ma_factor` | 均线因子表 | 每只 ETF 的 MA 均线趋势评分（多头/空头排列） |
 | `engine/factor/rsi_factor_engine.py` | `ods_market_kline` | `dwd_rsi_factor` | RSI 因子表 | 每只 ETF 的 RSI(6/12/24) 值及超买超卖评级 |
 | `engine/factor/drawdown_engine.py` | `ods_market_kline` | `dwd_drawdown_factor` | 回撤因子表 | 每只 ETF 从历史高点的最大回撤幅度及评分 |
 
 ---
 
 ### MACRO 层 — 宏观环境分析（2026-06 新增）
 
 双引擎模型：加权总分判定静态阶段 + 趋势加速度修正执行阶段。详细设计见 [macro-module-design.md](superpowers/specs/2026-06-18-macro-module-design.md)。
 
 | 模块文件 | 输入表 | 输出表 | 表中文名 | 业务含义 |
 |---|---|---|---|---|
 | `engine/macro/macro_indicator_engine.py` | `ods_macro_indicator` | `dwd_macro_indicator` | 宏观指标评分表 | 8 个宏观指标各自的 0-100 评分、趋势方向（上升/下降/持平）、评分说明 |
 | `engine/macro/macro_environment_engine.py` | `dwd_macro_indicator` | `dwd_macro_environment` | 宏观环境综合表 | 每日一行：加权宏观总分、静态阶段（扩张/复苏/观望/防御）、趋势加速度、修正后执行阶段、仓位上限% |
 
 ---
 
 ### SIGNAL 层 — 信号生成
 
 综合多个技术因子，生成 ETF 投资信号。
 
 | 模块文件 | 输入表 | 输出表 | 表中文名 | 业务含义 |
 |---|---|---|---|---|
 | `engine/signal/etf_signal_engine.py` | `dwd_ma_factor` + `dwd_rsi_factor` + `dwd_drawdown_factor` | `dwd_etf_signal` | ETF 综合信号表 | 三因子加权（MA 40% + RSI 30% + 回撤 30%）得出每只 ETF 的综合信号分和 S/A/B/C/D 等级 |
 | `engine/signal/signal_trend_engine.py` | `dwd_signal_history` | `dwd_signal_trend` | 信号趋势表 | 跟踪每只 ETF 信号分的历史趋势，判断信号是改善还是恶化 |
 
 ---
 
 ### STRATEGY 层 — 策略决策
 
 综合信号、持仓、宏观环境，生成投资建议。
 
 | 模块文件 | 输入表 | 输出表 | 表中文名 | 业务含义 |
 |---|---|---|---|---|
 | `engine/strategy/etf_score_engine_v2.py` | `dwd_etf_signal` + `dwd_floating_profit` + `dwd_allocation` + `dwd_macro_environment` | `dwd_etf_score_v2` | ETF 综合评分 V2 表 | 四因子加权（仓位分 20 + 浮盈分 15 + 收益分 15 + 宏观风向分 20）得出最终的 ETF 评分和 A/B/C/D 投资建议 |
 | `engine/strategy/add_position_engine.py` | `dwd_etf_score_v2` | `dwd_add_position_signal` | 加仓信号表 | 根据 ETF 评分生成是否加仓、加多少的建议 |
 | `engine/strategy/rebalance_engine_v2.py` | `dwd_category_allocation` | `dwd_rebalance_v2` | 调仓建议表 | 对比目标仓位与实际仓位，输出需要买入/卖出的 ETF 及数量 |
 | `engine/strategy/etf_overlap_engine.py` | `dwd_allocation` | `dwd_etf_overlap` | 重仓重叠表 | 检测持仓 ETF 的前十大重仓股重叠情况，提示集中度风险 |
 
 ---
 
 ### RISK 层 — 风险控制
 
 评估整体风险水平，集成宏观仓位上限。
 
 | 模块文件 | 输入表 | 输出表 | 表中文名 | 业务含义 |
 |---|---|---|---|---|
 | `engine/risk/risk_engine.py` | `dwd_allocation` + `dwd_category_allocation` + `dwd_macro_environment` | `dwd_risk_analysis` | 风险分析表 | 综合评估：宏观仓位上限 vs 实际仓位、集中度、波动率等风险指标 |
 | `engine/risk/position_health_engine.py` | `dwd_risk_analysis` | `dwd_position_health` | 持仓健康度表 | 持仓健康度打分，标记需要关注的风险点 |
 
 ---
 
 ### DASHBOARD 层 — 可视化展示
 
 单页面多视图，文件 `dashboard/home.py`，使用 Streamlit 渲染。
 
 | 视图标签 | 功能说明 | 读取的核心表 |
 |---|---|---|
 | 🏠 总览 | 宏观环境摘要卡（阶段/总分/加速度/仓位上限）+ 资产总览 | `dwd_macro_environment`、`dwd_allocation`、`dwd_floating_profit` |
 | 📊 持仓明细 | 每只 ETF 的成本、数量、盈亏、仓位占比 | `dwd_position`、`dwd_floating_profit`、`dwd_allocation` |
 | ⭐ ETF 评分 | 评分排行 + 宏观风向分列 + 加仓/调仓建议 | `dwd_etf_score_v2`、`dwd_add_position_signal` |
 | ⚠️ 风险分析 | 仓位上限仪表盘、超限警告、集中度风险 | `dwd_risk_analysis`、`dwd_position_health` |
 | 📝 每日复盘 | 当日操作回顾、信号变化、宏观阶段变动 | 多表汇总 |
 | 🗃️ 数据状态 | 各 ODS/DWD 表的数据量和最新时间 | 所有表 |
 | 🧠 投资决策中心 | AI 辅助决策对话 | 多表汇总 |
 
 ---
 
 ## 四、统一 Engine 规范
 
 所有 Engine（POSITION / FACTOR / MACRO / SIGNAL / STRATEGY / RISK）继承 `BaseEngine`（ETL 模式）：
 
 ```python
 class BaseEngine:
     def extract(self):   # 读数据：从上游表加载 DataFrame
     def transform(self): # 算：核心计算逻辑
     def load(self):      # 写：结果写入目标表
     def run(self):       # 串联：extract → transform → load，计时 + 打印
 ```
 
 ODS 加载器 **不继承** BaseEngine，直接使用 akshare + pandas + sqlite3 拉取外部数据。
 
 ---
 
 ## 五、批处理入口
 
 统一入口：`run_daily.py`
 
 ```bash
 python run_daily.py
 ```
 
 执行顺序：
 
 ```text
 ① 交易批量导入（tools/trade_watcher.py）
     ↓
 ② ODS 数据加载（成本→行情→K线→宏观）
     ↓
 ③ 持仓计算（成本→收益→浮盈→仓位→分类仓位）
     ↓
 ④ 技术因子计算（MA→RSI→回撤）
     ↓
 ⑤ 宏观分析（单指标评分→综合环境评分）
     ↓
 ⑥ 信号生成（ETF 综合信号→信号趋势）
     ↓
 ⑦ 策略决策（ETF 评分 V2→加仓→调仓→重叠分析）
     ↓
 ⑧ 风险控制（风险分析→持仓健康度）
     ↓
 ⑨ Dashboard 汇总
     ↓
 ⑩ 每日复盘
 ```
 
 ---
 
 ## 六、数据表总览
 
 ### ODS 层（4 张）
 
 | 表名 | 中文名 | 来源 | 写入策略 |
 |---|---|---|---|
 | `ods_trade_record` | 交易记录表 | 同花顺 Excel | 增量 INSERT，按 6 字段去重 |
 | `ods_market_price` | 行情快照表 | AKShare | 每日 DELETE + INSERT（全量刷新） |
 | `ods_market_kline` | K线历史表 | AKShare | 每日增量补充新交易日 |
 | `ods_macro_indicator` | 宏观指标原始表 | AKShare | 首次全量，后续按日期去重增量 |
 
 ### DWD 层（20 张）
 
 | 表名 | 中文名 | 所属层 | 写入策略 |
 |---|---|---|---|
 | `dwd_position` | 持仓明细表 | POSITION | 每日 DELETE + INSERT |
 | `dwd_profit_analysis` | 已实现收益表 | POSITION | 每日 DELETE + INSERT |
 | `dwd_floating_profit` | 浮动盈亏表 | POSITION | 每日 DELETE + INSERT |
 | `dwd_allocation` | 仓位分配表 | POSITION | 每日 DELETE + INSERT |
 | `dwd_category_allocation` | 分类仓位表 | POSITION | 每日 DELETE + INSERT |
 | `dwd_ma_factor` | 均线因子表 | FACTOR | 每日 DELETE + INSERT |
 | `dwd_rsi_factor` | RSI 因子表 | FACTOR | 每日 DELETE + INSERT |
 | `dwd_drawdown_factor` | 回撤因子表 | FACTOR | 每日 DELETE + INSERT |
 | `dwd_macro_indicator` | 宏观指标评分表 | MACRO | 每日增量（按日期+名称去重） |
 | `dwd_macro_environment` | 宏观环境综合表 | MACRO | 每日一行（按日期去重） |
 | `dwd_etf_signal` | ETF 综合信号表 | SIGNAL | 每日 DELETE + INSERT |
 | `dwd_signal_history` | 信号历史表 | SIGNAL | 每日增量（按日期去重） |
 | `dwd_signal_trend` | 信号趋势表 | SIGNAL | 每日 DELETE + INSERT |
 | `dwd_etf_score_v2` | ETF 综合评分 V2 表 | STRATEGY | 每日 DELETE + INSERT |
 | `dwd_add_position_signal` | 加仓信号表 | STRATEGY | 每日 DELETE + INSERT |
 | `dwd_rebalance` | 调仓建议表 | STRATEGY | 每日 DELETE + INSERT |
 | `dwd_rebalance_v2` | 调仓建议 V2 表 | STRATEGY | 每日 DELETE + INSERT |
 | `dwd_etf_overlap` | 重仓重叠表 | STRATEGY | 每日 DELETE + INSERT |
 | `dwd_risk_analysis` | 风险分析表 | RISK | 每日 DELETE + INSERT |
 | `dwd_position_health` | 持仓健康度表 | RISK | 每日 DELETE + INSERT |
 
 > **DELETE + INSERT**：每日全量覆盖，保证数据一致性  
 > **增量写入**：按组合键去重后 INSERT 新品，保留历史数据，用于回测和趋势分析
