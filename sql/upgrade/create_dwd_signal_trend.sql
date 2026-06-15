--评分趋势表------------------
--解释字段：
-- etf_code: ETF代码
-- etf_name: ETF名称
-- today_score: 今日评分
-- yesterday_score: 昨日评分
-- change_score: 变化评分
-- trend: 趋势
-- update_time: 更新时间

DROP TABLE IF EXISTS dwd_signal_trend;

CREATE TABLE dwd_signal_trend
(
    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    today_score REAL,

    yesterday_score REAL,

    change_score REAL,

    trend TEXT,

    update_time TEXT
);