 # 日经股东回报观察模块设计

 **Date**: 2026-06-25
 **Status**: Approved

 ## Problem

 日本企业在治理改革推动下（东证要求提升资本效率），回购和分红力度持续加大，直接影响日经 225 结构性吸引力。当前系统没有日本市场股东回报数据的观察能力，需要引入数据源做长期跟踪，后续可能作为日经 ETF 配置权重的因子。

 ## Scope

 - 从 JPX 拉取 Prime 板块分红与回购月度数据
 - 存储到 ODS 表，首次全量 + 后续增量
 - 新增 Dashboard 独立页面，展示分红/回购趋势
 - 纯观察，不做策略集成

 ## Non-Goals

 - 不接入策略/风险/宏观层（V1 仅供观察）
 - 不做个股级别数据（全市场汇总）
 - 不引入日经官网付费 API

 ## Architecture

 ### 数据流

 ```
 JPX 官网 Excel
     ↓
 ods/jpx_loader.py  ──→  ods_japan_return
     ↓
 dashboard/japan_return.py  ← 纯读表展示
 ```

 不接入 run_daily.py 流水线。JPX 数据月度更新，跑 pipeline 的时机和每日流水线不同，手动或独立定时触发。

 ### 目录结构

 ```
 ods/jpx_loader.py             ← 新增：爬取 JPX Excel，解析写入 ODS
 dashboard/japan_return.py     ← 新增：日经股东回报趋势图
 ```

 ## File Changes

 | 文件 | 动作 | 说明 |
 |---|---|---|
 | `ods/jpx_loader.py` | 新建 | 爬取 JPX Excel，解析 Prime 板块分红/回购数据 |
 | `dashboard/japan_return.py` | 新建 | 独立页面：折线图 + 同比柱状图 + 明细表 |

 ## Data Table

 ### ods_japan_return

 | 字段 | 类型 | 说明 |
 |---|---|---|
 | report_month | TEXT | 数据月份，格式 '2026-05' |
 | dividend_amount | REAL | Prime 板块月度分红总额（亿日元） |
 | buyback_amount | REAL | Prime 板块月度回购总额（亿日元） |
 | cum_dividend | REAL | 财年累计分红总额（亿日元） |
 | cum_buyback | REAL | 财年累计回购总额（亿日元） |
 | market | TEXT | 固定值 'Prime' |
 | source | TEXT | 固定值 'jpx' |
 | update_time | TEXT | 入库时间 |

 写入策略：按 `report_month` 去重。首次拉全量，后续每次只拉最近 3 个月。

 ## Data Source

 JPX「東証上場会社における配当・自社株買いの状況」月度 Excel。

 - URL：`https://www.jpx.co.jp/listing/stocks/dividend/`
 - 该页面包含 Excel 文件的直接链接，文件名通常为 `data_j.xls`
 - Excel 内含 Prime / Standard / Growth 三个板块的分红和回购数据
 - 本模块仅提取 Prime 板块的四项数值（月度分红、月度回购、累计分红、累计回购）

 ## Dashboard

 ### japan_return.py

 独立 Streamlit 页面，三块内容：

 1. **月度总额折线图**：分红金额（蓝线）+ 回购金额（红线），双轴
 2. **YoY 同比柱状图**：当月 vs 去年同月对比
 3. **近 12 月明细表**：日期、分红、回购、累计值

 从 `ods_japan_return` 读全部数据，前端排序和筛选。

 ## Weighting Philosophy

 V1 纯观察。后续评估是否纳入策略——若回购/分红数据显示持续上升趋势且与日经 ETF 收益正相关，则作为日经 ETF 配置因子的加分项。

 ## Dependencies

 `requests` + `openpyxl`（均已安装）——用于下载 JPX Excel 并解析。

 JPX 无 API 频率限制，月度更新，不构成负载。

 ## Testing

 - `tests/test_jpx_loader.py` — mock JPX Excel 返回，验证 Prime 板块数据解析和去重写入
 - `tests/test_japan_return_dashboard.py` — 验证页面正常渲染（图表 + 表格数据一致）
