-- ============================================================================
-- 表名: dwd_macro_environment
-- 用途: 宏观环境综合评分，含加权总分、静态阶段、趋势加速度、修正执行阶段、仓位上限
-- 字段说明:
--   eval_date:       评估日期 (主键)
--   macro_score:     宏观总分 (0-100)
--   macro_phase:     静态阶段 (扩张/复苏/观望/防御)
--   trend_score:     趋势加速度分
--   acceleration:    趋势加速度 (加速上升/加速下降/持平)
--   effective_phase: 修正后执行阶段
--   position_cap:    仓位上限 (%)
--   update_time:     更新时间
-- ============================================================================

DROP TABLE IF EXISTS dwd_macro_environment;

CREATE TABLE dwd_macro_environment (
    eval_date        TEXT PRIMARY KEY,
    macro_score      REAL,
    macro_phase      TEXT,
    trend_score      REAL,
    acceleration     TEXT,
    effective_phase  TEXT,
    position_cap     INTEGER,
    update_time      TEXT
);

CREATE INDEX IF NOT EXISTS idx_macro_env_date
    ON dwd_macro_environment (eval_date DESC);
