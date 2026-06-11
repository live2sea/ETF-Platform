# -*- coding: utf-8 -*-

"""
ETF平台每日任务调度

执行顺序：

1. 行情更新
2. 持仓分析
3. 仓位分析
4. 技术因子
5. 综合信号
6. 风险分析

作者: berton
"""

import time
from datetime import datetime

# ODS
from engine import rebalance_engine_v2
from ods.market_price_loader import MarketPriceLoader
from ods.market_kline_loader import MarketKlineLoader

# DWD
from engine.cost_engine import CostEngine
from engine.profit_engine import ProfitEngine

from engine.allocation_engine_v2 import AllocationEngine
from engine.allocation_category_engine_v2 import AllocationCategoryEngine

from engine.ma_factor_engine import MAFactorEngine
from engine.rsi_factor_engine import RSIFactorEngine
from engine.drawdown_engine import DrawdownEngine

from engine.etf_signal_engine import ETFSignalEngine

from engine.risk_engine import RiskEngine

from engine.add_position_engine import AddPositionEngine

from engine.rebalance_engine import RebalanceEngine

from engine.rebalance_engine_v2 import RebalanceEngineV2

class DailyRunner:

    def run_step(self, name, func):

        print()
        print("=" * 100)
        print(f"开始执行：{name}")
        print("=" * 100)

        start = time.time()

        try:

            func()

            cost = round(time.time() - start, 2)

            print(f"✓ 完成：{name}")
            print(f"耗时：{cost} 秒")

        except Exception as e:

            print(f"✗ 失败：{name}")
            print(f"原因：{e}")

            raise

    def run(self):

        start_time = datetime.now()

        print()
        print("=" * 100)
        print("ETF分析平台每日任务")
        print("=" * 100)

        # ==================================================
        # ODS
        # ==================================================

        self.run_step(
            "ETF实时行情更新",
            lambda: MarketPriceLoader().run()
        )

        self.run_step(
            "ETF历史K线更新",
            lambda: MarketKlineLoader().run()
        )

        # ==================================================
        # DWD
        # ==================================================

        self.run_step(
            "持仓成本计算",
            lambda: CostEngine().run()
        )

        self.run_step(
            "收益分析",
            lambda: ProfitEngine().run()
        )

        self.run_step(
            "仓位分析",
            lambda: AllocationEngine().run()
        )

        self.run_step(
            "主题仓位分析",
            lambda: AllocationCategoryEngine().run()
        )

        # ==================================================
        # FACTOR
        # ==================================================

        self.run_step(
            "MA趋势分析",
            lambda: MAFactorEngine().run()
        )

        self.run_step(
            "RSI分析",
            lambda: RSIFactorEngine().run()
        )

        self.run_step(
            "最大回撤分析",
            lambda: DrawdownEngine().run()
        )

        # ==================================================
        # SIGNAL
        # ==================================================

        self.run_step(
            "综合信号分析",
            lambda: ETFSignalEngine().run()
        )

        # ==================================================
        # RISK
        # ==================================================

        self.run_step(
            "组合风险分析",
            lambda: RiskEngine().run()
        )

        self.run_step(
            "加仓建议分析",
            lambda: AddPositionEngine().run()
        )

        self.run_step(
        "仓位再平衡",
            lambda: RebalanceEngineV2().run()
        )

        print()
        print("=" * 100)
        print("全部任务执行完成")
        print("=" * 100)

        end_time = datetime.now()

        print()
        print(f"开始时间：{start_time}")
        print(f"结束时间：{end_time}")

        print(
            f"总耗时："
            f"{round((end_time-start_time).total_seconds(),2)} 秒"
        )


if __name__ == "__main__":

    DailyRunner().run()