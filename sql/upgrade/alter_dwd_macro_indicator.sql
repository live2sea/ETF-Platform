DROP TABLE IF EXISTS dwd_macro_indicator;
CREATE TABLE dwd_macro_indicator (
    indicator_date  TEXT,
    indicator_name  TEXT,
    indicator_value REAL,
    score           INTEGER,
    trend           TEXT,
    comment         TEXT,
    update_time     TEXT,
    PRIMARY KEY (indicator_date, indicator_name)
);
