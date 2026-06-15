# -*- coding: utf-8 -*-

import time


# ==========================================
# ODS
# ==========================================

from ods.market_price_loader import MarketPriceLoader
from ods.market_kline_loader import MarketKlineLoader


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
from engine.signal.signal_history_engine import (
    SignalHistoryEngine
)
from engine.signal.signal_trend_engine import (
    SignalTrendEngine
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

        print(f"✓ 完成：{name}")
        print(f"耗时：{cost} 秒")

    except Exception as e:

        print(f"✗ 失败：{name}")
        print(e)


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

    # --------------------------------------
    # Position
    # --------------------------------------

    run_job(
        "持仓成本计算",
        CostEngine()
    )

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
        "信号历史快照",
        SignalHistoryEngine()
    )

    run_job(
        "信号趋势分析",
        SignalTrendEngine()
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