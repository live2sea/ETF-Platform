# -*- coding: utf-8 -*-

import streamlit as st
import plotly.express as px

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from _utils import load_df, rename_columns

st.title("📊 账户总览")

# ── KPI 行 ──
dashboard_df = load_df("SELECT * FROM dwd_dashboard")
db = dict(zip(dashboard_df["item_name"], dashboard_df["item_value"]))

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("总成本", db.get("总成本", "--"))
c2.metric("总市值", db.get("总市值", "--"))
c3.metric("总盈亏", db.get("总盈亏", "--"))
c4.metric("收益率", db.get("收益率", "--"))
c5.metric("高风险项", db.get("高风险项数量", "--"))

st.divider()

# ── 仓位结构 ──
st.subheader("📦 类别仓位结构")

cat_df = load_df(
    "SELECT category_name, market_value, allocation_pct, etf_count, risk_level "
    "FROM dwd_category_allocation ORDER BY allocation_pct DESC"
)

col_a, col_b = st.columns([1, 1])
with col_a:
    fig = px.pie(cat_df, names="category_name", values="allocation_pct",
                 hole=0.35, title="仓位占比")
    st.plotly_chart(fig, use_container_width=True)
with col_b:
    fig = px.bar(cat_df, x="category_name", y="allocation_pct",
                 color="risk_level", title="各类别仓位")
    st.plotly_chart(fig, use_container_width=True)

st.dataframe(rename_columns(cat_df), use_container_width=True, hide_index=True)

st.divider()

# ── 关键信号 ──
st.subheader("📡 关键信号")

r1, r2 = st.columns(2)
r1.metric("第一重仓", db.get("第一重仓", "--"))
r1.metric("最佳 ETF", db.get("最佳ETF", "--"))
r2.metric("推荐加仓", db.get("推荐加仓", "--"))
r2.metric("偏离最大仓位", db.get("偏离最大仓位", "--"))

st.divider()

# ── 摘要 ──
st.subheader("📋 今日摘要")
lines = [f"当前收益率：{db.get('收益率', '--')}"]
if not cat_df.empty:
    top = cat_df.iloc[0]
    lines.append(f"最大仓位类别：{top['category_name']} ({top['allocation_pct']:.1f}%)")
    high = cat_df[cat_df["risk_level"] == "高风险"]
    if not high.empty:
        lines.append(f"高风险分类数：{len(high)}")
lines.append(f"最强 ETF：{db.get('最佳ETF', '--')}")
lines.append(f"优先关注：{db.get('推荐加仓', '--')}")
st.success("\n\n".join(lines))

st.caption("数据来源：dwd_dashboard / dwd_category_allocation")