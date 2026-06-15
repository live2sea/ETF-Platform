-- ============================================================================
-- 表名: dwd_drawdown_factor
-- 用途: 52周回撤因子，计算当前价相对52周高点的回撤幅度
-- 字段说明:
--   etf_code:      ETF代码 (主键)
--   etf_name:      ETF名称
--   current_price:  当前价格
--   high_52w:       52周最高价
--   low_52w:        52周最低价
--   drawdown_pct:   回撤百分比 (负值)
--   score:          回撤评分 (0-100，回撤越大分数越高)
--   level:          等级 (S/A/B/C/D)
--   signal:         操作信号
--   update_time:    更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_drawdown_factor;

CREATE TABLE dwd_drawdown_factor (
    etf_code      TEXT PRIMARY KEY,
    etf_name      TEXT,
    current_price REAL,
    high_52w      REAL,
    low_52w       REAL,
    drawdown_pct  REAL,
    score         INTEGER,
    level         TEXT,
    signal        TEXT,
    update_time   TEXT
);
