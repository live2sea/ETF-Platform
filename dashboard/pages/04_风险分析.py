# -*- coding: utf-8 -*-

import streamlit as st
import plotly.express as px

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from _utils import load_df, rename_columns

st.title("⚠️ 风险分析")

risk_df = load_df("SELECT * FROM dwd_risk_analysis")
health_df = load_df("SELECT * FROM dwd_position_health")

# ── 账户健康度 ──
st.subheader("❤️ 账户健康度")
if not health_df.empty:
    st.dataframe(rename_columns(health_df), use_container_width=True, hide_index=True)
else:
    st.info("暂无数据")

st.divider()

# ── 风险分布 (图+表并排) ──
col_a, col_b = st.columns([1, 1])
with col_a:
    st.subheader("风险等级分布")
    if not risk_df.empty:
        level_counts = risk_df.groupby("risk_level").size().reset_index(name="count")
        fig = px.pie(level_counts, names="risk_level", values="count", title="风险等级",
                     color="risk_level",
                     color_discrete_map={"高风险": "#dc2626", "中风险": "#eab308", "低风险": "#16a34a"})
        st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("风险值排行")
    if not risk_df.empty:
        fig = px.bar(risk_df.sort_values("risk_value", ascending=False),
                     x="risk_name", y="risk_value", color="risk_level",
                     title="风险项排序",
                     color_discrete_map={"高风险": "#dc2626", "中风险": "#eab308", "低风险": "#16a34a"})
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── 风险明细 ──
st.subheader("风险项明细")
if not risk_df.empty:
    st.dataframe(rename_columns(risk_df), use_container_width=True, hide_index=True)

    high_risk = risk_df[risk_df["risk_level"].isin(["高风险", "HIGH", "H"])]
    if not high_risk.empty:
        st.error(f"⚠ 发现 {len(high_risk)} 项高风险！")
        st.dataframe(rename_columns(high_risk), use_container_width=True, hide_index=True)
    else:
        st.success("当前无高风险项目")
else:
    st.info("暂无风险分析数据")

st.divider()

# ── 点评 ──
st.subheader("📋 风险点评")
if not risk_df.empty:
    high_count = len(risk_df[risk_df["risk_level"].isin(["高风险", "HIGH", "H"])])
    top_risk = risk_df.nlargest(1, "risk_value").iloc[0]
    lines = [
        f"风险项总数：{len(risk_df)}",
        f"高风险项数：{high_count}",
        f"最大风险源：{top_risk['risk_name']}（{top_risk['risk_level']}）",
        f"建议：{top_risk['suggestion']}",
    ]
    if high_count == 0:
        lines.append("整体风险可控。")
    elif high_count <= 2:
        lines.append("存在局部风险，建议重点关注。")
    else:
        lines.append("风险偏高，建议逐步优化仓位结构。")
    st.info("\n\n".join(lines))


st.divider()

# === macro position cap gauge ===
macro_df = load_df("SELECT * FROM dwd_macro_environment ORDER BY eval_date DESC LIMIT 1")
if not macro_df.empty:
    mr = macro_df.iloc[0]
    cap = int(mr["position_cap"])
    active_phase = mr.get("effective_phase", mr["macro_phase"])
    st.subheader(f"🛡 仓位上限仪表盘 (phase={active_phase}, cap={cap}%)")
    # Get actual total allocation
    alloc_df = load_df("SELECT SUM(allocation_pct) as total FROM dwd_allocation")
    actual = float(alloc_df.iloc[0]["total"]) if not alloc_df.empty else 0
    gap = round(actual - cap, 1)
    c1, c2, c3 = st.columns(3)
    c1.metric("仓位上限", f"{cap}%")
    c2.metric("实际仓位", f"{actual:.1f}%")
    c3.metric("超限幅度", f"{gap:.1f}%", delta=f"{gap:.1f}%" if gap != 0 else None, delta_color="inverse")
    if gap > 0:
        st.error(f"🚨 仓位超限警告: 实际仓位({actual:.1f}%)超过上限({cap}%){gap:.1f}%，建议减仓!")
    else:
        st.success(f"✅ 仓位正常: 实际仓位({actual:.1f}%)低于上限({cap}%)")

st.caption("数据来源：dwd_risk_analysis / dwd_position_health")