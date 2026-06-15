-- ==========================================
-- ETF历史信号快照
-- ==========================================

-- 解释字段：
-- trade_date: 交易日期
-- etf_code: ETF代码
-- etf_name: ETF名称
-- ma_score: 均线评分
-- rsi_score: RSI评分
-- drawdown_score: 回撤评分
-- signal_score: 综合信号评分
-- level: 信号等级
-- suggestion: 操作建议
-- update_time: 更新时间

DROP TABLE IF EXISTS dwd_signal_history;

CREATE TABLE dwd_signal_history (

    trade_date TEXT,

    etf_code TEXT,

    etf_name TEXT,

    ma_score INTEGER,

    rsi_score INTEGER,

    drawdown_score INTEGER,

    signal_score REAL,

    level TEXT,

    suggestion TEXT,

    update_time TEXT,

    PRIMARY KEY (
        trade_date,
        etf_code
    )

);