DROP TABLE IF EXISTS dwd_etf_signal;

CREATE TABLE dwd_etf_signal
(
    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    ma_score INTEGER,
    rsi_score INTEGER,
    drawdown_score INTEGER,

    signal_score REAL,

    level TEXT,

    suggestion TEXT,

    update_time TEXT
);