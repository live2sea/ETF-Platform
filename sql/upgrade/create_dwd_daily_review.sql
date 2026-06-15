-- ============================================================================
-- 表名: dwd_daily_review
-- 用途: 每日复盘报告，汇总当日总资产/最佳/最差ETF/AI总结等
-- 字段说明:
--   review_item:  复盘项名称 (主键)
--   review_value: 复盘项内容
--   update_time:  更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_daily_review;

CREATE TABLE dwd_daily_review (
    review_item  TEXT PRIMARY KEY,
    review_value TEXT,
    update_time  TEXT
);
