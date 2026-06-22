-- ============================================================================
-- 表名: dwd_dashboard_history
-- 用途: Dashboard历史快照，每日保存关键指标用于资产曲线和历史趋势
-- 字段说明:
--   trade_date:    交易日期 (主键)
--   total_cost:    总成本
--   total_market:  总市值
--   total_profit:  总盈亏
--   profit_pct:    收益率 (%)
--   best_etf:      最佳ETF
--   recommend_etf: 推荐加仓ETF
--   risk_count:    高风险项数量
--   update_time:   更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_dashboard_history;

CREATE TABLE dwd_dashboard_history (
    trade_date    TEXT PRIMARY KEY,
    total_cost    REAL,
    total_market  REAL,
    total_profit  REAL,
    profit_pct    REAL,
    best_etf      TEXT,
    recommend_etf TEXT,
    risk_count    INTEGER,
    update_time   TEXT
);
