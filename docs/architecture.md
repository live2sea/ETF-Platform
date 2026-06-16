# ETF-Platform 系统架构设计文档

## 一、项目目标

ETF-Platform 是个人ETF投资分析平台。

主要目标：

* 自动导入交易记录
* 自动计算持仓成本
* 自动计算收益
* 自动计算技术指标
* 自动生成投资信号
* 自动生成调仓建议
* 自动生成每日复盘
* Dashboard可视化展示

---

## 二、系统总体架构

```text
ODS
 ↓
POSITION
 ↓
FACTOR
 ↓
SIGNAL
 ↓
STRATEGY
 ↓
RISK
 ↓
REVIEW
 ↓
DASHBOARD
```

---

## 三、模块说明

### ODS层

负责原始数据采集。

目录：

```text
ods/
```

模块：

* trade_import.py
* market_price_loader.py
* market_kline_loader.py

输出表：

* ods_trade_record
* ods_market_price
* ods_market_kline

---

### POSITION层

负责持仓计算。

目录：

```text
engine/position/
```

模块：

* cost_engine.py
* profit_engine.py
* floating_profit_engine.py
* allocation_engine.py
* allocation_category_engine_v2.py

输出表：

* dwd_position
* dwd_profit_analysis
* dwd_floating_profit
* dwd_allocation
* dwd_category_allocation

---

### FACTOR层

负责技术指标计算。

目录：

```text
engine/factor/
```

模块：

* ma_factor_engine.py
* rsi_factor_engine.py
* drawdown_engine.py

输出表：

* dwd_ma_factor
* dwd_rsi_factor
* dwd_drawdown_factor

---

### SIGNAL层

负责生成ETF信号。

目录：

```text
engine/signal/
```

模块：

* etf_signal_engine.py
* signal_history_engine.py
* signal_trend_engine.py

输出表：

* dwd_etf_signal
* dwd_signal_history
* dwd_signal_trend

---

### STRATEGY层

负责投资决策。

目录：

```text
engine/strategy/
```

模块：

* etf_score_engine_v2.py
* add_position_engine.py
* rebalance_engine.py
* rebalance_engine_v2.py
* etf_overlap_engine.py

输出表：

* dwd_etf_score_v2
* dwd_add_position_signal
* dwd_rebalance
* dwd_rebalance_v2
* dwd_etf_overlap

---

### RISK层

负责风险分析。

目录：

```text
engine/risk/
```

模块：

* risk_engine.py
* position_health_engine.py

输出表：

* dwd_risk_analysis
* dwd_position_health

---

### REVIEW层

负责每日复盘。

目录：

```text
engine/review/
```

模块：

* review_engine.py

输出表：

* dwd_daily_review

---

### DASHBOARD层

负责可视化展示。

目录：

```text
dashboard/
```

模块：

* Home.py
* 01_总览.py
* 02_持仓分析.py
* 03_ETF评分.py
* 04_风险分析.py
* 05_调仓建议.py
* 06_ETF排行榜.py
* 07_ETF详情.py
* 08_AI投资决策中心.py
* 09_交易复盘中心.py

---

## 四、统一Engine规范

所有Engine继承：

```python
class BaseEngine:

    def extract(self):
        pass

    def transform(self):
        pass

    def load(self):
        pass

    def run(self):
        self.extract()
        self.transform()
        self.load()
```

统一执行流程：

```text
Extract
 ↓
Transform
 ↓
Load
```

---

## 五、批处理入口

统一入口：

```text
run_daily.py
```

每日执行：

```bash
python run_daily.py
```
