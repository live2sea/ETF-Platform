 # ETF-Platform

 个人 ETF 投资分析平台。自动导入交易记录、计算持仓与收益、生成投资信号与调仓建议，并通过 Streamlit 仪表盘展示。

 ## 快速启动

 ```bash
 # 1. 创建并激活虚拟环境
 python -m venv venv
 venv\Scripts\activate        # Windows

 # 2. 安装依赖
 pip install -r requirements.txt

 # 3. 初始化数据库
 sqlite3 data/etf.db < sql/init_db.sql

 # 4. 运行每日流水线
 python run_daily.py

 # 5. 启动仪表盘
 streamlit run dashboard/home.py
 ```

 ## 目录

 ```
 ods/         原始数据拉取（行情、K线、宏观）
 engine/      核心引擎（持仓 → 因子 → 宏观 → 信号 → 策略 → 风险）
 dashboard/   Streamlit 仪表盘
 config/      评分权重配置文件
 docs/        架构文档 & 设计 spec
 sql/         数据库建表 & 升级脚本
 tests/       单元测试 & 集成测试
 tools/       辅助工具（交易 Excel 批量导入）
 ```

 ## 文档

 | 文档 | 说明 |
 |---|---|
 | [docs/architecture.md](docs/architecture.md) | 系统架构全景图、模块说明、数据表总览 |
 | [docs/superpowers/specs/](docs/superpowers/specs/) | 各模块详细设计 spec |

 ## 依赖

 ```
 akshare==1.18.64    # 行情 & 宏观数据
 pandas==2.3.0       # 数据处理
 streamlit==1.45.1   # 仪表盘
 openpyxl==3.1.5     # Excel 读写
 watchdog==6.0.0     # 文件监控（交易 Excel 自动导入）
 ```
