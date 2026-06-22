## sql/upgrade/ 建表规范

### 文件命名

每个表一份文件，命名为 `create_{table_name}.sql`，只保留最新完整建表语句，**不**另建 `alter_*` 文件。

### 文件结构

```
-- ============================================================================
-- 表名: {table_name}
-- 用途: {一句话说明}
-- 字段说明:
--   col1:      说明
--   col2:      说明
--   主键:      (col1, col2)          -- 复合主键时注明
-- ============================================================================

DROP TABLE IF EXISTS {table_name};

CREATE TABLE {table_name} (
    col1 类型 PRIMARY KEY,
    col2 类型,
    ...
);

CREATE INDEX IF NOT EXISTS idx_xxx ON {table_name} (...);  -- 按需
```

### 规则

1. **注释头必须** — 表名、用途、字段说明、主键标注，用 `-- ===...===` 分隔
2. **列名对齐** — 列名与类型间留 2-4 空格，同表中最大列名对齐
3. **列间无空行** — `CREATE TABLE` 内字段定义连续书写，不插入空行
4. **主键必设** — 单列用 `TEXT PRIMARY KEY`，复合用末尾 `PRIMARY KEY (a, b)`
5. **一份建表** — 最新完整 DDL，不用 DROP+CREATE 充当 ALTER，不保留 alter 文件
6. **前缀匹配层** — `create_ods_*` 对应 ODS 层，`create_dwd_*` 对应 DWD 层
