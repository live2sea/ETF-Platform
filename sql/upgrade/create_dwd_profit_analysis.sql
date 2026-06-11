DROP TABLE IF EXISTS dwd_profit_analysis;
--  =====================================
-- 盈亏分析表
-- 该表用于存储每只ETF的盈亏分析结果，包括ETF代码、名称、持仓数量、平均成本、已实现盈亏、盈亏排名和更新时间等字段。
-- 该表的数据将通过对当前持仓表和原始交易记录进行计算和分析得到，用于评估每只ETF的盈亏情况和排名，帮助投资者了解投资组合的表现。
CREATE TABLE dwd_profit_analysis(

    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    quantity INTEGER,

    avg_cost REAL,

    realized_profit REAL,

    profit_rank INTEGER,

    update_time TEXT
);