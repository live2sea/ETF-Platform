DROP TABLE IF EXISTS ods_trade_record;
--------------------------------------
-- 原始交易记录表
-- 该表用于存储从券商平台导出的ETF交易记录，包含交易的基本信息，如交易日期、时间、ETF代码、名称、交易类型、数量、价格、金额、费用、税费和结算金额等。
-- 该表的数据将作为后续数据处理和分析的基础，确保交易记录的完整性和准确性。
CREATE TABLE ods_trade_record(
--  唯一标识符，自动递增        
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_date TEXT,

    trade_time TEXT,

    etf_code TEXT,

    etf_name TEXT,

    trade_type TEXT,

    quantity INTEGER,

    price REAL,

    amount REAL,

    fee REAL,

    tax REAL,

    settlement_amount REAL
);



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

-- =====================================
-- 当前仓位结构分析表
-- =====================================

DROP TABLE IF EXISTS dwd_allocation;

CREATE TABLE dwd_allocation (

    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    quantity INTEGER,

    avg_cost REAL,

    current_price REAL,

    cost_value REAL,

    market_value REAL,

    allocation_pct REAL,

    update_time TEXT

);

-- ==========================================
-- 国家 / 主题仓位分析
-- ==========================================

DROP TABLE IF EXISTS dwd_category_allocation;
CREATE TABLE dwd_category_allocation (

    category_name TEXT PRIMARY KEY,

    market_value REAL,

    allocation_pct REAL,

    etf_count INTEGER,

    risk_level TEXT,

    update_time TEXT

);

-- ==========================================
-- 市场价格表
DROP TABLE IF EXISTS ods_market_price;

CREATE TABLE ods_market_price (

    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    fund_type TEXT,

    current_price REAL,

    update_time TEXT

);

--==========================================
-- 浮盈浮亏分析表

DROP TABLE IF EXISTS dwd_floating_profit;

CREATE TABLE dwd_floating_profit (

    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    quantity INTEGER,

    avg_cost REAL,

    current_price REAL,

    cost_value REAL,

    market_value REAL,

    floating_profit REAL,

    floating_profit_pct REAL,

    update_time TEXT

);





--=========================================
-- 综合评分表
--========================================= 
DROP TABLE IF EXISTS dwd_etf_score;

CREATE TABLE dwd_etf_score (

    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    category_name TEXT,

    allocation_pct REAL,

    floating_profit REAL,

    floating_profit_pct REAL,

    realized_profit REAL,

    total_score INTEGER,

    score_level TEXT,

    suggestion TEXT,

    update_time TEXT

);

--=========================================
-- 综合评分表v2 
DROP TABLE IF EXISTS dwd_etf_score_v2;

CREATE TABLE dwd_etf_score_v2 (

    etf_code TEXT PRIMARY KEY,
    etf_name TEXT,

    category_name TEXT,

    allocation_pct REAL,

    floating_profit REAL,
    floating_profit_pct REAL,

    realized_profit REAL,

    trend_score INTEGER,
    rsi_score INTEGER,
    allocation_score INTEGER,
    floating_score INTEGER,
    realized_score INTEGER,

    total_score INTEGER,

    score_level TEXT,

    suggestion TEXT,

    update_time TEXT

);


--=========================================
-- 市场K线数据表    
DROP TABLE IF EXISTS ods_market_kline;

CREATE TABLE ods_market_kline (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    etf_code TEXT NOT NULL,

    etf_name TEXT,

    trade_date TEXT NOT NULL,

    open_price REAL,

    high_price REAL,

    low_price REAL,

    close_price REAL,

    volume REAL,

    amount REAL,

    update_time TEXT

);

CREATE INDEX idx_kline_code_date
ON ods_market_kline(etf_code, trade_date);

DROP TABLE IF EXISTS dwd_ma_factor;

CREATE TABLE dwd_ma_factor (

    etf_code TEXT PRIMARY KEY,

    etf_name TEXT,

    trade_date TEXT,

    close_price REAL,

    ma20 REAL,

    ma60 REAL,

    ma120 REAL,

    ma250 REAL,

    trend_score INTEGER,

    trend_level TEXT,

    signal TEXT,

    update_time TEXT

);