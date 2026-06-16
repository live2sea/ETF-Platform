# -*- coding: utf-8 -*-

import streamlit as st
import plotly.express as px

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from _utils import load_df, rename_columns

st.title("⚖️ 调仓建议")

# ── 数据（全部走 load_df 缓存） ──
rebalance_df = load_df(
    "SELECT * FROM dwd_rebalance_v2 ORDER BY ABS(deviation_pct) DESC"
)
add_df = load_df(
    "SELECT etf_code, etf_name, final_score, recommend_amount, recommendation "
    "FROM dwd_add_position_signal WHERE recommend_amount > 0 ORDER BY final_score DESC"
)

# ── 类别偏离 ──
st.subheader("📐 资产类别偏离")
if not rebalance_df.empty:
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.dataframe(rename_columns(rebalance_df), use_container_width=True, hide_index=True)
    with col_b:
        fig = px.bar(rebalance_df.sort_values("deviation_pct"),
                     x="category", y="deviation_pct", color="action",
                     title="各类别偏离度",
                     color_discrete_map={"加仓": "#16a34a", "减仓": "#dc2626"})
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("暂无调仓数据")

st.divider()

# ── 加仓建议 ──
st.subheader("💰 加仓建议")
if not add_df.empty:
    top5 = add_df.head(5)
    cols = st.columns(5)
    for i, (_, row) in enumerate(top5.iterrows()):
        cols[i].metric(row["etf_name"], f"{row['final_score']:.0f}分",
                       f"建议 {row['recommend_amount']:,.0f}")

    st.dataframe(rename_columns(add_df), use_container_width=True, hide_index=True)
else:
    st.info("当前无推荐加仓 ETF")

st.divider()

# ── 决策摘要 ──
st.subheader("📋 决策摘要")
lines = []

if not rebalance_df.empty:
    top_dev = rebalance_df.iloc[0]
    lines.append(f"偏离最大类别：{top_dev['category']}（{top_dev['deviation_pct']:.1f}%）→ {top_dev['action']}")

if not add_df.empty:
    best_add = add_df.iloc[0]
    lines.append(f"首选加仓：{best_add['etf_name']}（{best_add['final_score']:.0f}分，建议 {best_add['recommend_amount']:,.0f}）")
    over_70 = add_df[add_df["final_score"] >= 70]
    lines.append(f"高分加仓标的数：{len(over_70)}")

st.success("\n\n".join(lines))

st.caption("数据来源：dwd_rebalance_v2 / dwd_add_position_signal")