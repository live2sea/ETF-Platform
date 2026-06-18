-- Table: ods_macro_indicator
DROP TABLE IF EXISTS ods_macro_indicator;
CREATE TABLE ods_macro_indicator (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator_date  TEXT,
    indicator_name  TEXT,
    indicator_value REAL,
    source          TEXT,
    update_time     TEXT
);
CREATE INDEX IF NOT EXISTS idx_ods_macro_date_name ON ods_macro_indicator (indicator_date, indicator_name);
