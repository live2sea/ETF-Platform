CREATE TABLE IF NOT EXISTS dwd_position_health
(
    health_item TEXT PRIMARY KEY,

    item_value REAL,

    risk_level TEXT,

    suggestion TEXT,

    update_time TEXT
);