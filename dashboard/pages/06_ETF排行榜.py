# -*- coding: utf-8 -*-

import streamlit as st
import plotly.express as px

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from _utils import load_df, rename_columns

st.title("📊 因子排行榜")

# 焦点：按因子维度排名，与 03_ETF评分 的综合评分区分
ma_df = load_df(
    "SELECT etf_code, etf_name, trend_score, trend_level, signal "
    "FROM dwd_ma_factor ORDER BY trend_score DESC"
)
rsi_df = load_df(
    "SELECT etf_code, etf_name, rsi6, score, signal "
    "FROM dwd_rsi_factor ORDER BY rsi6 ASC"
)
dd_df = load_df(
    "SELECT etf_code, etf_name, drawdown_pct, score, signal "
    "FROM dwd_drawdown_factor ORDER BY drawdown_pct ASC"
)

# ── MA 趋势 ──
st.subheader("📈 MA 趋势榜")
if not ma_df.empty:
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.dataframe(rename_columns(ma_df[["etf_name", "trend_score", "trend_level", "signal"]]),
                     use_container_width=True, hide_index=True)
    with col_b:
        fig = px.bar(ma_df.head(15), x="etf_name", y="trend_score",
                     color="trend_level", title="MA 趋势评分 TOP15",
                     color_discrete_map={"强": "#16a34a", "中": "#eab308", "弱": "#dc2626"})
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── RSI 超卖 ──
st.subheader("📉 RSI 超卖榜（低 RSI = 超卖信号）")
if not rsi_df.empty:
    col_c, col_d = st.columns([1, 1])
    with col_c:
        st.dataframe(rename_columns(rsi_df[["etf_name", "rsi6", "score", "signal"]]),
                     use_container_width=True, hide_index=True)
    with col_d:
        fig = px.bar(rsi_df.head(15), x="etf_name", y="rsi6",
                     color="signal", title="RSI 超卖 TOP15",
                     color_discrete_map={"超卖": "#16a34a", "中性": "#eab308", "超买": "#dc2626"})
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── 回撤 ──
st.subheader("💎 回撤价值榜（深回撤 = 潜在买点）")
if not dd_df.empty:
    col_e, col_f = st.columns([1, 1])
    with col_e:
        st.dataframe(rename_columns(dd_df[["etf_name", "drawdown_pct", "score", "signal"]]),
                     use_container_width=True, hide_index=True)
    with col_f:
        fig = px.bar(dd_df.head(15), x="etf_name", y="drawdown_pct",
                     color="signal", title="回撤深度 TOP15")
        st.plotly_chart(fig, use_container_width=True)

st.caption("数据来源：dwd_ma_factor / dwd_rsi_factor / dwd_drawdown_factor")