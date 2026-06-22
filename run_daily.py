# -*- coding: utf-8 -*-
"""ETF Daily Batch Pipeline.
Processes pending trade Excel files (incremental import + dedup) at pipeline start.
"""


import time



# ==========================================
# Trade Auto-Import
from tools.trade_watcher import run as run_trade_watcher

# ODS
# ==========================================

from ods.market_price_loader import MarketPriceLoader
from ods.market_kline_loader import MarketKlineLoader
from ods.macro_loader      import MacroLoader


# ==========================================
# Position
# ==========================================

from engine.position.cost_engine import CostEngine
from engine.position.profit_engine import ProfitEngine
from engine.position.floating_profit_engine import FloatingProfitEngine
from engine.position.allocation_engine import AllocationEngine
from engine.position.allocation_category_engine_v2 import (
    AllocationCategoryEngine
)


# ==========================================
# Factor
# ==========================================

from engine.factor.ma_factor_engine import MAFactorEngine
from engine.factor.rsi_factor_engine import RSIFactorEngine
from engine.factor.drawdown_engine import DrawdownEngine


# ==========================================
# Signal
# ==========================================

from engine.signal.etf_signal_engine import ETFSignalEngine

from engine.signal.signal_trend_engine import (
    SignalTrendEngine
)


# ==========================================
# Macro
# ==========================================

from engine.macro.macro_indicator_engine import (
    MacroIndicatorEngine
)

from engine.macro.macro_environment_engine import (
    MacroEnvironmentEngine
)


# ==========================================
# Strategy
# ==========================================

from engine.strategy.etf_score_engine_v2 import (
    ETFScoreEngineV2
)

from engine.strategy.add_position_engine import (
    AddPositionEngine
)

from engine.strategy.rebalance_engine import (
    RebalanceEngine
)

from engine.strategy.rebalance_engine_v2 import (
    RebalanceEngineV2
)

from engine.strategy.etf_overlap_engine import (
    ETFOverlapEngine
)


# ==========================================
# Risk
# ==========================================

from engine.risk.position_health_engine import (
    PositionHealthEngine
)

from engine.risk.risk_engine import (
    RiskEngine
)


# ==========================================
# Dashboard
# ==========================================


from engine.dashboard.dashboard_engine import (
    DashboardEngine
)

from engine.dashboard.dashboard_history_engine import (
    DashboardHistoryEngine
)


# ==========================================
# Review
# ==========================================

from engine.review.review_engine import (
    ReviewEngine
)


# ==========================================
# 执行器
# ==========================================

def run_job(name, engine):

    print()
    print("=" * 80)
    print(name)
    print("=" * 80)

    start = time.time()

    try:

        engine.run()

        cost = round(
            time.time() - start,
            2
        )

        print(f"[OK] {name} 完成，耗时 {cost}s")

    except Exception as e:

        print(f"[FAIL] {name}")
        import traceback
        traceback.print_exc()


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":

    total_start = time.time()

    print()
    print("=" * 80)
    print("ETF DAILY BATCH START")
    print("=" * 80)

    # --------------------------------------
    # --------------------------------------
    # 批量导入积压的交易 Excel
    # --------------------------------------

    print()
    print("=" * 80)
    print("trade_watcher: 扫描导入交易Excel")
    print("=" * 80)

    run_trade_watcher()

    # --------------------------------------
    # 先把数据加载到position表，ods层逻辑依赖这个表，后续再优化成并行
    # --------------------------------------

    run_job(
        "持仓成本计算",
        CostEngine()
    )

    # --------------------------------------
    # Trade Auto-Import


# ODS
    # --------------------------------------

    run_job(
        "市场价格更新",
        MarketPriceLoader()
    )

    run_job(
        "K线更新",
        MarketKlineLoader()
    )

    run_job(
        "宏观指标拉取",
        MacroLoader()
    )

    # --------------------------------------
    # Position
    # --------------------------------------

    run_job(
        "已实现收益分析",
        ProfitEngine()
    )

    run_job(
        "浮盈浮亏分析",
        FloatingProfitEngine()
    )

    run_job(
        "ETF仓位分析",
        AllocationEngine()
    )

    run_job(
        "分类仓位分析",
        AllocationCategoryEngine()
    )

    # --------------------------------------
    # Factor
    # --------------------------------------

    run_job(
        "MA趋势分析",
        MAFactorEngine()
    )

    run_job(
        "RSI分析",
        RSIFactorEngine()
    )

    run_job(
        "回撤分析",
        DrawdownEngine()
    )

    # --------------------------------------
    # Signal
    # --------------------------------------

    run_job(
        "ETF综合信号",
        ETFSignalEngine()
    )



    run_job(
        "信号趋势分析",
        SignalTrendEngine()
    )

    # --------------------------------------
    # Macro
    # --------------------------------------

    run_job(
        "宏观指标评分",
        MacroIndicatorEngine()
    )

    run_job(
        "宏观环境评估",
        MacroEnvironmentEngine()
    )

    # --------------------------------------
    # Strategy
    # --------------------------------------

    run_job(
        "ETF评分V2",
        ETFScoreEngineV2()
    )

    run_job(
        "加仓建议",
        AddPositionEngine()
    )

    run_job(
        "调仓建议",
        RebalanceEngine()
    )

    run_job(
        "分类调仓建议",
        RebalanceEngineV2()
    )

    run_job(
        "ETF重仓重叠分析",
        ETFOverlapEngine()
    )

    # --------------------------------------
    # Risk
    # --------------------------------------

    run_job(
        "持仓健康度",
        PositionHealthEngine()
    )

    run_job(
        "风险分析",
        RiskEngine()
    )

    # --------------------------------------
    # Dashboard
    # --------------------------------------

    run_job(
        "Dashboard汇总",
        DashboardEngine()
    )

    run_job(
        "Dashboard历史快照",
        DashboardHistoryEngine()
    )

    # --------------------------------------
    # Review
    # --------------------------------------

    run_job(
        "每日复盘",
        ReviewEngine()
    )

    # --------------------------------------
    # Finish
    # --------------------------------------

    total_cost = round(
        time.time() - total_start,
        2
    )

    print()
    print("=" * 80)
    print("ETF DAILY BATCH FINISHED")
    print("=" * 80)

    print(f"总耗时：{total_cost} 秒")
