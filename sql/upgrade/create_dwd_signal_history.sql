-- ============================================================================
-- 表名: dwd_signal_history
-- 用途: ETF信号历史快照，按日保存每次信号计算结果的完整记录
-- 字段说明:
--   trade_date:      交易日期
--   etf_code:        ETF代码
--   etf_name:        ETF名称
--   ma_score:        MA因子得分
--   rsi_score:       RSI因子得分
--   drawdown_score:  回撤因子得分
--   signal_score:    综合信号得分
--   level:           信号等级
--   suggestion:      操作建议
--   update_time:     更新时间
--   主键:            (trade_date, etf_code)
-- ============================================================================

DROP TABLE IF EXISTS dwd_signal_history;

CREATE TABLE dwd_signal_history (
    trade_date      TEXT,
    etf_code        TEXT,
    etf_name        TEXT,
    ma_score        INTEGER,
    rsi_score       INTEGER,
    drawdown_score  INTEGER,
    signal_score    REAL,
    level           TEXT,
    suggestion      TEXT,
    update_time     TEXT,
    PRIMARY KEY (trade_date, etf_code)
);
