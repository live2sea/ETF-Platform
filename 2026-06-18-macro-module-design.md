 # Macro 模块设计

 **Date**: 2026-06-18
 **Status**: Approved

 ## Problem

 当前 `engine/macro/` 只有一个文件 `macro_indicator_engine.py`，数据硬编码在 `extract()` 里，未接入 AKShare，不在 `run_daily.py` 流水线中，也不对策略和风险模块产生任何影响。需要一个完整的宏观分析模块，从外部拉取数据、评分、输出到策略和风险决策。

 ## Scope

 - 从 AKShare 拉取 8 个核心宏观指标
 - 单指标评分（0-100）→ 综合宏观环境评分 + 趋势加速度
 - 宏观评分驱动：总仓位上限（Risk 层）+ 单 ETF 风向加分（Strategy 层）
 - 权重和阈值集中配置，支持后续回测调优
 - 不改变现有模块的职责边界，仅在 ETF 评分和风险引擎中追加字段

 ## Non-Goals

 - 不做实时宏观数据推送/通知
 - 不做 Dashboard 新增宏观页面（后续独立 spec）
 - 不做机器学习预测模型
 - 不引入 Tushare/FRED/Wind 等额外数据源（V1 只用 AKShare）

 ## Architecture

 ### 双引擎模型

 **引擎一（静态水平）**：8 个宏观指标加权求和 → 宏观总分(0-100) → 映射到四阶段（扩张/复苏/观望/防御）。

 **引擎二（趋势加速度）**：跟踪各指标近 3 个月变化方向，汇总趋势分 → 趋势正向/负向时修正一档实际执行阶段。

 - 正向加速：提前一档执行（如观望期 → 按复苏期运行）
 - 负向加速：提前一档防御（如复苏期 → 按观望期运行）
 - 中性：严格按加权总分阶段执行
 - 最多修正一档，不跨档跳跃

 ### 数据流

 ```
 AKShare API
     ↓
 ods/macro_loader.py  ──→  ods_macro_indicator      (原始数据，含日期)
     ↓
 engine/macro/macro_indicator_engine.py  ──→  dwd_macro_indicator  (单指标评分)
     ↓
 engine/macro/macro_environment_engine.py  ──→  dwd_macro_environment  (综合分+加速度+阶段)
     ↓                         ↘
 engine/strategy/etf_score_engine_v2.py    engine/risk/risk_engine.py
 ```

 ### 流水线位置（run_daily.py）

 ```
 ODS 层:
   4 MacroLoader                     ← 新增

 MACRO 引擎层:
 12 MacroIndicatorEngine            ← 新增
 13 MacroEnvironmentEngine          ← 新增

 STRATEGY 层:
 15 ETFScoreEngineV2                ← 修改（读 effective_phase）

 RISK 层:
 19 RiskEngine                      ← 修改（读 position_cap）
 ```

 ## File Changes

 | 文件 | 动作 | 说明 |
 |---|---|---|
 | `ods/macro_loader.py` | 新建 | 从 AKShare 拉取 8 个宏观指标，写入 ods_macro_indicator |
 | `engine/macro/macro_indicator_engine.py` | 修改 | extract 改为读 ODS 表；load 改为增量快照(按日期去重) |
 | `engine/macro/macro_environment_engine.py` | 新建 | 加权总分 + 趋势加速度 + 阶段判定 |
 | `config/macro_weights.json` | 新建 | 指标权重、评分区间、ETF风向映射、阶段阈值 |
 | `engine/strategy/etf_score_engine_v2.py` | 修改 | 新增宏观风向分(第4项，0-20分)，总分上限 50→70 |
 | `engine/risk/risk_engine.py` | 修改 | 新增 position_cap / cap_gap / cap_warning |
 | `run_daily.py` | 修改 | 插入 3 段 macro 任务 |

 ## Data Tables

 ### ods_macro_indicator

 | 字段 | 类型 | 说明 |
 |---|---|---|
 | indicator_date | TEXT | 指标日期 |
 | indicator_name | TEXT | 指标名称 |
 | indicator_value | REAL | 原始值 |
 | source | TEXT | AKShare 函数名 |
 | update_time | TEXT | 更新时间 |

 ### dwd_macro_indicator

 | 字段 | 类型 | 说明 |
 |---|---|---|
 | indicator_date | TEXT | 指标日期 |
 | indicator_name | TEXT | 指标名称 |
 | indicator_value | REAL | 原始值 |
 | score | INTEGER | 评分(0-100) |
 | trend | TEXT | 上升/下降/持平 |
 | comment | TEXT | 评分说明 |
 | update_time | TEXT | 更新时间 |

 增量写入，按 `(indicator_date, indicator_name)` 去重。不再 DELETE ALL。

 ### dwd_macro_environment

 | 字段 | 类型 | 说明 |
 |---|---|---|
 | eval_date | TEXT | 评估日期 |
 | macro_score | REAL | 加权总分(0-100) |
 | macro_phase | TEXT | 静态阶段(扩张/复苏/观望/防御) |
 | trend_score | REAL | 趋势加速度分(-1~1) |
 | acceleration | TEXT | 正向/负向/中性 |
 | effective_phase | TEXT | 趋势修正后的实际执行阶段 |
 | position_cap | INTEGER | 仓位上限 % |
 | update_time | TEXT | 更新时间 |

 每日一行。

 ## Config: macro_weights.json

 六个配置段：

 1. `indicators` — 指标名称 → AKShare 函数名 + 权重
 2. `phase_thresholds` — 扩张≥75 / 复苏≥60 / 观望≥40 / 防御<40
 3. `phase_position_caps` — 各阶段仓位上限
 4. `trend` — 回溯月数 / 正负加速度阈值
 5. `score_ranges` — 每个指标的 raw → score 分段线性映射（含正向/反向类型）
 6. `etf_category_bonus` — 各阶段 × ETF 类型的加分映射

 详见文件本身。

 ## Scoring Logic

 ### 单指标评分（分段线性插值）

 8 个指标各设 3-5 个 raw→score 锚点，区间内线性插值。配置中 `type: "反向"` 表示值越小分数越高（美联储利率、PE）。

 | 指标 | 高分(80-100) | 中性(50-70) | 低分(0-40) |
 |---|---|---|---|
 | PMI | ≥52 | 50-52 | <48 |
 | M2 同比 | ≥12% | 8-12% | <8% |
 | 中美利差 | >0% | -2~0% | <-3% |
 | CPI 年率 | 1-3% | -1~1% 或 3-4% | <-1% 或 >5% |
 | PPI 年率 | 0-3% | -3~0% 或 3-5% | <-3% 或 >7% |
 | 美联储利率 | ≤3% | 3-5% | >5% |
 | 沪深300 PE | <12 | 12-18 | >18 |
 | 北向月度净流入 | >500亿 | 0-500亿 | <0 |

 ### 综合评分

 ```
 macro_score = Σ(单指标分数 × 权重)
 ```

 ### 趋势加速度

 ```
 trend_score = Σ(sign(当前值 - N月前值) × 权重)
 trend_score > +0.15 → 正向加速
 trend_score < -0.15 → 负向加速
 其余 → 中性
 ```

 ### 阶段修正矩阵

 | 静态阶段 → 趋势 | 正向 | 中性 | 负向 |
 |---|---|---|---|
 | 防御期(<40) | 观望期 | 防御期 | 防御期 |
 | 观望期(40-59) | 复苏期 | 观望期 | 防御期 |
 | 复苏期(60-74) | 扩张期 | 复苏期 | 观望期 |
 | 扩张期(≥75) | 扩张期 | 扩张期 | 复苏期 |

 ## ETF Score Integration

 `etf_score_engine_v2.py` 改后公式：

 ```
 总得分 = 仓位分(20) + 浮盈分(15) + 收益分(15) + 宏观风向分(20)
 ```

 ETF 类型映射沿用现有 `_category_map`。未匹配类型默认 +10。

 评档阈值同步缩放（50→70）：

 | 等级 | 新阈值 |
 |---|---|
 | A 优先加仓 | ≥55 |
 | B 继续持有 | ≥45 |
 | C 观察 | ≥35 |
 | D 减仓观察 | <35 |

 ## Risk Engine Integration

 `risk_engine.py` 新增字段：

 - `macro_position_cap` — 当前阶段仓位上限
 - `cap_gap` — 实际仓位 − 上限
 - `cap_warning` — gap > 0 时生成减仓建议

 ## Weighting Philosophy

 V1 使用主观初始权重（经济理论 + A 股经验），所有权重集中在 `config/macro_weights.json` 中，方便后续回测调参。V2 用回测引擎校准：

 1. 历史宏观数据 × 持仓 ETF 净值 → 相关性分析，重定指标权重
 2. 标注各历史阶段，统计各类 ETF 实际收益分布 → 校准 ETF 风向加分表
 3. 网格搜索最优加速度阈值

 ## Dependencies

 AKShare 1.18.64（已安装）— 8 个接口均已实测可用。

 ## Testing

 - `tests/test_macro_loader.py` — mock AKShare 返回，验证 8 个指标入库
 - `tests/test_macro_indicator_engine.py` — 给定 ODS 数据，验证评分计算、增量写入、去重
 - `tests/test_macro_environment_engine.py` — 给定 dwd_macro_indicator，验证加权总分、趋势加速度、阶段修正
 - `tests/test_etf_score_macro.py` — 给定 effective_phase，验证各类 ETF 加分正确
 - `tests/test_macro_integration.py` — 端到端：模拟 3 个宏观日，验证流水线产出
