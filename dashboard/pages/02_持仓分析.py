# -*- coding: utf-8 -*-

import streamlit as st
import plotly.express as px

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from _utils import load_df, rename_columns, style_dataframe

st.title("💼 持仓分析")

# ── 数据 ──
pos_df = load_df(
    "SELECT p.etf_code, p.etf_name, p.quantity, p.avg_cost, "
    "f.current_price, f.market_value, f.floating_profit, f.floating_profit_pct "
    "FROM dwd_position p LEFT JOIN dwd_floating_profit f ON p.etf_code=f.etf_code "
    "ORDER BY f.market_value DESC"
)

allocation_df = load_df(
    "SELECT etf_code, etf_name, market_value, allocation_pct "
    "FROM dwd_allocation ORDER BY allocation_pct DESC"
)

if pos_df.empty:
    st.warning("暂无持仓数据")
    st.stop()

# ── 持仓总览表 ──
st.subheader("当前持仓明细")
st.dataframe(rename_columns(pos_df), use_container_width=True, hide_index=True)

st.divider()

# ── 盈亏排行 (并排) ──
profit_top = pos_df.nlargest(10, "floating_profit")
loss_top = pos_df.nsmallest(10, "floating_profit")

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("🟢 盈利 TOP10")
    fig = px.bar(profit_top, x="etf_name", y="floating_profit",
                 title="盈利排行", color="floating_profit",
                 color_continuous_scale=["#86efac", "#16a34a"])
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("🔴 亏损 TOP10")
    fig = px.bar(loss_top, x="etf_name", y="floating_profit",
                 title="亏损排行", color="floating_profit",
                 color_continuous_scale=["#fca5a5", "#dc2626"])
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── 仓位占比 ──
st.subheader("仓位占比")
fig = px.pie(allocation_df, names="etf_name", values="allocation_pct",
             hole=0.35, title="ETF 仓位占比")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── 三指标 ──
best = pos_df.nlargest(1, "floating_profit_pct").iloc[0]
worst = pos_df.nsmallest(1, "floating_profit_pct").iloc[0]
largest = allocation_df.iloc[0] if not allocation_df.empty else None

c1, c2, c3 = st.columns(3)
c1.metric("最佳 ETF", best["etf_name"], f"{best['floating_profit_pct']:.2f}%")
c2.metric("最弱 ETF", worst["etf_name"], f"{worst['floating_profit_pct']:.2f}%")
if largest is not None:
    c3.metric("第一重仓", largest["etf_name"], f"{largest['allocation_pct']:.2f}%")

st.divider()

# ── 点评 ──
st.subheader("📋 持仓点评")
profit_count = int((pos_df["floating_profit"] > 0).sum())
lines = [
    f"持仓 ETF 数量：{len(pos_df)}",
    f"盈利 ETF 数量：{profit_count}",
    f"最佳：{best['etf_name']} (+{best['floating_profit_pct']:.2f}%)",
    f"最弱：{worst['etf_name']} ({worst['floating_profit_pct']:.2f}%)",
]
if largest is not None:
    lines.append(f"第一重仓：{largest['etf_name']} ({largest['allocation_pct']:.2f}%)")
st.success("\n\n".join(lines))

st.caption("数据来源：dwd_position / dwd_floating_profit / dwd_allocation")