# ETF-Platform 数据流转文档

## 一、原始数据

### 交易记录

```text
Excel
 ↓
trade_import.py
 ↓
ods_trade_record
```

---

### 行情数据

```text
AKShare
 ↓
market_price_loader.py
 ↓
ods_market_price
```

```text
AKShare
 ↓
market_kline_loader.py
 ↓
ods_market_kline
```

---

## 二、持仓链路

```text
ods_trade_record
 ↓
cost_engine
 ↓
dwd_position
```

---

## 三、收益链路

```text
dwd_position
 +
ods_market_price
 ↓
floating_profit_engine
 ↓
dwd_floating_profit
```

---

## 四、仓位链路

```text
dwd_floating_profit
 ↓
allocation_engine
 ↓
dwd_allocation
```

```text
dwd_allocation
 ↓
allocation_category_engine_v2
 ↓
dwd_category_allocation
```

---

## 五、技术指标链路

```text
ods_market_kline
 ↓
ma_factor_engine
 ↓
dwd_ma_factor
```

```text
ods_market_kline
 ↓
rsi_factor_engine
 ↓
dwd_rsi_factor
```

```text
ods_market_kline
 ↓
drawdown_engine
 ↓
dwd_drawdown_factor
```

---

## 六、信号链路

```text
MA
 +
RSI
 +
Drawdown
 ↓
etf_signal_engine
 ↓
dwd_etf_signal
```

---

## 七、历史信号

```text
dwd_etf_signal
 ↓
signal_history_engine
 ↓
dwd_signal_history
```

---

## 八、趋势分析

```text
dwd_signal_history
 ↓
signal_trend_engine
 ↓
dwd_signal_trend
```

---

## 九、策略链路

```text
dwd_etf_signal
 +
dwd_floating_profit
 +
dwd_allocation
 ↓
etf_score_engine_v2
 ↓
dwd_etf_score_v2
```

---

### 加仓建议

```text
dwd_etf_score_v2
 ↓
add_position_engine
 ↓
dwd_add_position_signal
```

---

### 调仓建议

```text
dwd_category_allocation
 ↓
rebalance_engine_v2
 ↓
dwd_rebalance_v2
```

---

## 十、风险链路

```text
dwd_allocation
 ↓
risk_engine
 ↓
dwd_risk_analysis
```

```text
dwd_risk_analysis
 ↓
position_health_engine
 ↓
dwd_position_health
```

---

## 十一、复盘链路

```text
全部DWD结果
 ↓
review_engine
 ↓
dwd_daily_review
```
