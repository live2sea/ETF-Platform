-- ============================================================================
-- 表名: dwd_etf_signal
-- 用途: ETF综合信号，加权汇总MA/RSI/回撤三个因子评分
-- 字段说明:
--   etf_code:        ETF代码 (主键)
--   etf_name:        ETF名称
--   ma_score:        MA因子得分
--   rsi_score:       RSI因子得分
--   drawdown_score:  回撤因子得分
--   signal_score:    综合信号得分 (MA*0.4 + RSI*0.3 + 回撤*0.3)
--   level:           信号等级 (S/A/B/C/D)
--   suggestion:      操作建议
--   update_time:     更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_etf_signal;

CREATE TABLE dwd_etf_signal (
    etf_code        TEXT PRIMARY KEY,
    etf_name        TEXT,
    ma_score        INTEGER,
    rsi_score       INTEGER,
    drawdown_score  INTEGER,
    signal_score    REAL,
    level           TEXT,
    suggestion      TEXT,
    update_time     TEXT
);
