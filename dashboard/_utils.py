"""
ETF Dashboard 共享工具
"""
import sqlite3
import pandas as pd
from pathlib import Path

_ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = str(_ROOT_DIR / "data" / "etf.db")


def load_df(query, params=None):
    conn = sqlite3.connect(DB_PATH)
    try:
        return pd.read_sql(query, conn, params=params)
    finally:
        conn.close()


COLUMN_LABELS = {
    "etf_code": "代码",
    "etf_name": "ETF名称",
    "quantity": "持仓数量",
    "avg_cost": "持仓成本",
    "current_price": "当前价格",
    "market_value": "市值",
    "cost_value": "成本",
    "floating_profit": "浮动盈亏",
    "floating_profit_pct": "收益率%",
    "allocation_pct": "占比%",
    "signal_score": "综合评分",
    "ma_score": "MA评分",
    "rsi_score": "RSI评分",
    "drawdown_score": "回撤评分",
    "trend_score": "趋势评分",
    "trend_level": "趋势等级",
    "level": "等级",
    "suggestion": "建议",
    "signal": "信号",
    "recommendation": "操作建议",
    "recommend_amount": "建议金额",
    "final_score": "最终评分",
    "trade_date": "日期",
    "update_time": "更新时间",
    "category_name": "分类",
    "risk_level": "风险等级",
    "risk_type": "风险类型",
    "risk_name": "风险名称",
    "risk_value": "风险值",
    "category": "类别",
    "current_pct": "当前占比%",
    "target_pct": "目标占比%",
    "deviation_pct": "偏离度%",
    "action": "操作方向",
    "suggest_amount": "建议调仓额",
    "health_item": "指标",
    "item_value": "数值",
    "item_name": "指标名称",
    "etf_count": "ETF数量",
    "macro_bonus": "宏观风向分",
    "macro_score": "宏观总分",
    "macro_phase": "宏观阶段",
    "effective_phase": "执行阶段",
    "acceleration": "趋势加速",
    "position_cap": "仓位上限",
    "cap_gap": "超限幅度",
    "positive_cap": "建议仓位",
    "actual_pct": "实际仓位",
}


def rename_columns(df):
    mapping = {k: v for k, v in COLUMN_LABELS.items() if k in df.columns}
    return df.rename(columns=mapping)


def color_profit(val):
    if isinstance(val, (int, float)):
        if val > 0:
            return "color: #16a34a"
        elif val < 0:
            return "color: #dc2626"
    return ""


def style_dataframe(df, profit_cols=None):
    if profit_cols is None:
        profit_cols = [c for c in df.columns if any(
            kw in str(c).lower() for kw in ["profit", "盈亏", "收益率", "pct", "评分", "score"]
        )]
    styled = df.style
    for col in profit_cols:
        if col in df.columns:
            styled = styled.map(color_profit, subset=[col])
    return styled
