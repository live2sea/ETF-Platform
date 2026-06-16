# -*- coding: utf-8 -*-

import streamlit as st
import plotly.express as px
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from _utils import load_df, rename_columns

st.title("🏆 ETF 综合评分")

signal_df = load_df(
    "SELECT etf_code, etf_name, ma_score, rsi_score, drawdown_score, "
    "signal_score, level, suggestion FROM dwd_etf_signal ORDER BY signal_score DESC"
)

if signal_df.empty:
    st.warning("暂无评分数据")
    st.stop()

# ── TOP3 ──
top3 = signal_df.head(3)
c1, c2, c3 = st.columns(3)
medals = ["🥇", "🥈", "🥉"]
for i, (col, medal) in enumerate(zip([c1, c2, c3], medals)):
    if i < len(top3):
        row = top3.iloc[i]
        col.metric(f"{medal} {row['etf_name']}", f"{row['signal_score']:.0f} 分", row["level"])

st.divider()

# ── 评分表 + 图 并排 ──
col_a, col_b = st.columns([1, 1])
with col_a:
    st.subheader("评分排名")
    st.dataframe(rename_columns(signal_df), use_container_width=True, hide_index=True)
with col_b:
    st.subheader("TOP15 综合评分")
    fig = px.bar(signal_df.head(15), x="etf_name", y="signal_score", color="level",
                 title="综合评分 TOP15",
                 color_discrete_map={"强": "#16a34a", "中": "#eab308", "弱": "#dc2626"})
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── 等级分布 + 评分拆解 ──
col_c, col_d = st.columns([1, 1])
with col_c:
    level_counts = signal_df.groupby("level").size().reset_index(name="count")
    fig = px.pie(level_counts, names="level", values="count",
                 title="等级分布", color="level",
                 color_discrete_map={"强": "#16a34a", "中": "#eab308", "弱": "#dc2626"})
    st.plotly_chart(fig, use_container_width=True)

with col_d:
    st.subheader("评分拆解")
    selected = st.selectbox("选择 ETF 查看详情", signal_df["etf_name"])
    detail = signal_df[signal_df["etf_name"] == selected].iloc[0]
    score_df = pd.DataFrame({
        "因子": ["MA 趋势", "RSI 位置", "回撤空间"],
        "评分": [detail["ma_score"], detail["rsi_score"], detail["drawdown_score"]]
    })
    fig = px.bar(score_df, x="因子", y="评分", title=f"{selected} 因子拆解",
                 color="评分", color_continuous_scale=["#fca5a5", "#fbbf24", "#16a34a"])
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── 关注名单 + 点评 ──
focus_df = signal_df[signal_df["signal_score"] >= 70]
col_e, col_f = st.columns([1, 1])
with col_e:
    st.subheader("⭐ 重点关注 (评分 ≥ 70)")
    if not focus_df.empty:
        st.dataframe(rename_columns(focus_df[["etf_code", "etf_name", "signal_score", "level", "suggestion"]]),
                     use_container_width=True, hide_index=True)
    else:
        st.info("暂无高分 ETF")

with col_f:
    st.subheader("📋 投资建议")
    best = signal_df.iloc[0]
    worst = signal_df.iloc[-1]
    st.info(
        f"**最强**：{best['etf_name']} — {best['signal_score']:.0f} 分 ({best['level']})\n\n"
        f"建议：{best['suggestion']}\n\n---\n\n"
        f"**最弱**：{worst['etf_name']} — {worst['signal_score']:.0f} 分 ({worst['level']})\n\n"
        f"建议：{worst['suggestion']}\n\n---\n\n"
        f"评分由 MA 趋势 + RSI 位置 + 回撤空间综合计算。"
    )

st.caption("数据来源：dwd_etf_signal")