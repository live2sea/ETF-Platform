
DROP TABLE IF EXISTS dwd_position;

-- 当前持仓表   
-- 该表用于存储当前持有的ETF仓位信息，包括ETF代码、名称、持仓数量、平均成本、买入金额、卖出金额、已实现盈亏和更新时间等字段。
-- 该表的数据将通过对原始交易记录进行计算和汇总得到，用于分析当前的持仓情况和盈亏情况。
CREATE TABLE dwd_position(

    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    quantity INTEGER,

    avg_cost REAL,

    buy_amount REAL,

    sell_amount REAL,

    realized_profit REAL,

    update_time TEXT
);