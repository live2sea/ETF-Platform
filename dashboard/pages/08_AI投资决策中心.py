# -*- coding: utf-8 -*-

import streamlit as st
import plotly.express as px

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from _utils import load_df, rename_columns

st.title("🤖 投资决策中心")

# ── 今日复盘摘要 ──
st.subheader("📋 今日复盘摘要")
review_df = load_df("SELECT * FROM dwd_daily_review")
if not review_df.empty:
    rmap = dict(zip(review_df["review_item"], review_df["review_value"]))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("总资产", rmap.get("总资产", "--"))
    c2.metric("总盈亏", rmap.get("总盈亏", "--"))
    c3.metric("收益率", rmap.get("收益率", "--"))
    c4.metric("最佳 ETF", rmap.get("最佳ETF", "--"))
    # AI 总结
    ai = rmap.get("AI总结", "")
    if ai:
        st.success(ai)
else:
    st.info("暂无复盘数据")

st.divider()

# ── 加仓建议 ──
st.subheader("💰 推荐加仓")
add_df = load_df(
    "SELECT * FROM dwd_add_position_signal ORDER BY final_score DESC"
)
add_show = add_df[add_df["recommend_amount"] > 0] if not add_df.empty else add_df
if not add_show.empty:
    top_add = add_show.iloc[0]
    st.info(
        f"**首选加仓**：{top_add['etf_code']} {top_add['etf_name']}  "
        f"| 评分 {top_add['final_score']:.0f}  |  建议 {top_add['recommend_amount']:,.0f}"
    )
    st.dataframe(rename_columns(add_show), use_container_width=True, hide_index=True)
else:
    st.info("当前无推荐加仓 ETF")

st.divider()

# ── 调仓 + 风险 并排 ──
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("⚖️ 调仓建议")
    rebalance_df = load_df(
        "SELECT * FROM dwd_rebalance_v2 ORDER BY ABS(deviation_pct) DESC"
    )
    if not rebalance_df.empty:
        st.dataframe(rename_columns(rebalance_df), use_container_width=True, hide_index=True)
    else:
        st.info("暂无调仓建议")

with col_b:
    st.subheader("🚨 风险预警")
    risk_df = load_df("SELECT * FROM dwd_risk_analysis")
    if not risk_df.empty:
        high_risk = risk_df[risk_df["risk_level"].isin(["高风险", "HIGH", "H"])]
        if not high_risk.empty:
            st.error(f"{len(high_risk)} 项高风险")
            st.dataframe(rename_columns(high_risk), use_container_width=True, hide_index=True)
        else:
            st.success("当前无高风险项")
    else:
        st.info("暂无风险数据")

st.divider()

# ── 综合建议 ──
st.subheader("🎯 综合建议")
lines = []
if not add_show.empty:
    best = add_show.iloc[0]
    lines.append(f"首选加仓：{best['etf_name']}（{best['final_score']:.0f}分）")
if not rebalance_df.empty:
    top = rebalance_df.iloc[0]
    lines.append(f"调仓优先：{top['category']} {top['action']}（偏离 {top['deviation_pct']:.1f}%）")
if lines:
    st.success("\n\n".join(lines))
else:
    st.info("暂无明确操作建议")

st.caption("数据来源：dwd_daily_review / dwd_add_position_signal / dwd_rebalance_v2 / dwd_risk_analysis")