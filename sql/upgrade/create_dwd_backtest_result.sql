-- ============================================================================
-- 表名: dwd_backtest_result
-- 用途: 策略回测结果，存储每只ETF的回测绩效指标
-- 字段说明:
--   strategy_name: 策略名称
--   etf_code:      ETF代码
--   etf_name:      ETF名称
--   trade_count:   交易次数
--   win_count:     获胜次数
--   win_rate:      胜率 (%)
--   total_return:  总收益率 (%)
--   annual_return: 年化收益率 (%)
--   max_drawdown:  最大回撤 (%)
--   sharpe_ratio:  夏普比率
--   update_time:   更新时间
--   主键:          (strategy_name, etf_code)
-- ============================================================================

DROP TABLE IF EXISTS dwd_backtest_result;

CREATE TABLE dwd_backtest_result (
    strategy_name TEXT,
    etf_code      TEXT,
    etf_name      TEXT,
    trade_count   INTEGER,
    win_count     INTEGER,
    win_rate      REAL,
    total_return  REAL,
    annual_return REAL,
    max_drawdown  REAL,
    sharpe_ratio  REAL,
    update_time   TEXT,
    PRIMARY KEY (strategy_name, etf_code)
);
