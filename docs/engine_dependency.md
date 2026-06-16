# ETF-Platform Engine依赖关系

## 一级依赖

```text
trade_import
market_price_loader
market_kline_loader
```

无依赖。

---

## Position层

```text
cost_engine
依赖:
ods_trade_record
```

```text
profit_engine
依赖:
ods_trade_record
```

```text
floating_profit_engine
依赖:
dwd_position
ods_market_price
```

```text
allocation_engine
依赖:
dwd_floating_profit
```

```text
allocation_category_engine_v2
依赖:
dwd_allocation
```

---

## Factor层

```text
ma_factor_engine
依赖:
ods_market_kline
```

```text
rsi_factor_engine
依赖:
ods_market_kline
```

```text
drawdown_engine
依赖:
ods_market_kline
```

---

## Signal层

```text
etf_signal_engine
依赖:

dwd_ma_factor
dwd_rsi_factor
dwd_drawdown_factor
```

```text
signal_history_engine
依赖:

dwd_etf_signal
```

```text
signal_trend_engine
依赖:

dwd_signal_history
```

---

## Strategy层

```text
etf_score_engine_v2
依赖:

dwd_etf_signal
dwd_floating_profit
dwd_allocation
```

```text
add_position_engine
依赖:

dwd_etf_score_v2
```

```text
rebalance_engine_v2
依赖:

dwd_category_allocation
```

```text
etf_overlap_engine
依赖:

dwd_allocation
```

---

## Risk层

```text
risk_engine
依赖:

dwd_allocation
dwd_category_allocation
```

```text
position_health_engine
依赖:

dwd_risk_analysis
```

---

## Dashboard层

```text
dashboard_engine
依赖:

全部核心DWD表
```

---

## Review层

```text
review_engine
依赖:

dashboard结果
策略结果
风险结果
```

---

## run_daily执行顺序

```text
ODS

1 MarketPriceLoader
2 MarketKlineLoader

POSITION

3 CostEngine
4 ProfitEngine
5 FloatingProfitEngine
6 AllocationEngine
7 AllocationCategoryEngine

FACTOR

8 MAFactorEngine
9 RSIFactorEngine
10 DrawdownEngine

SIGNAL

11 ETFSignalEngine
12 SignalHistoryEngine
13 SignalTrendEngine

STRATEGY

14 ETFScoreEngineV2
15 AddPositionEngine
16 RebalanceEngineV2
17 ETFOverlapEngine

RISK

18 RiskEngine
19 PositionHealthEngine

DASHBOARD

20 DashboardEngine

REVIEW

21 ReviewEngine
```
