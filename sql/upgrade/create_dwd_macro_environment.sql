DROP TABLE IF EXISTS dwd_macro_environment;
CREATE TABLE dwd_macro_environment (
    eval_date       TEXT PRIMARY KEY,
    macro_score     REAL,
    macro_phase     TEXT,
    trend_score     REAL,
    acceleration    TEXT,
    effective_phase TEXT,
    position_cap    INTEGER,
    update_time     TEXT
);
