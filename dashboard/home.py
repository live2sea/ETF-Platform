# -*- coding: utf-8 -*-

import streamlit as st
import plotly.express as px

from _utils import load_df, rename_columns

# ==================================================
st.set_page_config(
    page_title="ETF交易分析平台",
    page_icon="📈",
    layout="wide"
)

st.title("📈 ETF交易分析平台")
st.caption("个人量化投资驾驶舱 —— 数据每日由 run_daily.py 自动更新")

# ── KPI ──
dashboard_df = load_df("SELECT * FROM dwd_dashboard")
dashboard = dict(zip(dashboard_df["item_name"], dashboard_df["item_value"]))

c1, c2, c3, c4 = st.columns(4)
c1.metric("总成本", dashboard.get("总成本", "--"))
c2.metric("总市值", dashboard.get("总市值", "--"))
c3.metric("总盈亏", dashboard.get("总盈亏", "--"))
c4.metric("收益率", dashboard.get("收益率", "--"))

st.divider()

# ── 仓位结构 ──
st.subheader("🌍 资产配置")
allocation_df = load_df(
    "SELECT category_name, market_value, allocation_pct, etf_count, risk_level "
    "FROM dwd_category_allocation ORDER BY allocation_pct DESC"
)

col_a, col_b = st.columns([1, 1])
with col_a:
    fig = px.pie(allocation_df, values="market_value", names="category_name",
                 hole=0.4, title="各类别仓位占比")
    st.plotly_chart(fig, use_container_width=True)
with col_b:
    fig = px.bar(allocation_df, x="category_name", y="allocation_pct",
                 color="risk_level", title="各类别仓位占比 (柱状)")
    st.plotly_chart(fig, use_container_width=True)

st.dataframe(rename_columns(allocation_df), use_container_width=True, hide_index=True)

st.divider()

# ── ETF 信号 ──
st.subheader("🏆 ETF 信号一览")
signal_df = load_df(
    "SELECT etf_code, etf_name, signal_score, level, suggestion "
    "FROM dwd_etf_signal ORDER BY signal_score DESC"
)
fig = px.bar(signal_df.head(15), x="etf_name", y="signal_score",
             color="level", title="ETF 综合评分 TOP15",
             color_discrete_map={"强": "#16a34a", "中": "#eab308", "弱": "#dc2626"})
st.plotly_chart(fig, use_container_width=True)
st.dataframe(rename_columns(signal_df), use_container_width=True, hide_index=True)

st.divider()

# ── 持仓 ──
st.subheader("📦 当前持仓")
pos_df = load_df(
    "SELECT etf_code, etf_name, quantity, avg_cost, current_price, "
    "market_value, floating_profit, floating_profit_pct, update_time "
    "FROM dwd_floating_profit ORDER BY market_value DESC"
)
st.dataframe(rename_columns(pos_df), use_container_width=True, hide_index=True)
st.caption(f"数据更新时间：{pos_df['update_time'].max() if not pos_df.empty else 'N/A'}")
