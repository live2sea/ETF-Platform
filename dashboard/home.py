# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

DB_PATH = "data/etf.db"


# ==================================================
# 数据读取
# ==================================================
@st.cache_data(ttl=60)
def load_table(table_name):

    conn = sqlite3.connect(DB_PATH)

    try:
        return pd.read_sql(
            f"select * from {table_name}",
            conn
        )

    finally:
        conn.close()


# ==================================================
# 页面配置
# ==================================================
st.set_page_config(
    page_title="ETF交易分析平台",
    page_icon="📈",
    layout="wide"
)

st.title("📈 ETF交易分析平台")

st.caption("个人量化投资驾驶舱")


# ==================================================
# Dashboard
# ==================================================
dashboard_df = load_table(
    "dwd_dashboard"
)

dashboard = dict(
    zip(
        dashboard_df["item_name"],
        dashboard_df["item_value"]
    )
)

# ==================================================
# 顶部指标
# ==================================================
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "总成本",
    dashboard.get("总成本", 0)
)

col2.metric(
    "总市值",
    dashboard.get("总市值", 0)
)

col3.metric(
    "总盈亏",
    dashboard.get("总盈亏", 0)
)

col4.metric(
    "收益率",
    dashboard.get("收益率", "0%")
)

st.divider()


# ==================================================
# 仓位结构
# ==================================================
allocation_df = load_table(
    "dwd_category_allocation"
)

st.subheader("🌍 国家 / 主题配置")

fig = px.pie(
    allocation_df,
    values="market_value",
    names="category_name",
    hole=0.4
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.dataframe(
    allocation_df,
    use_container_width=True
)

st.divider()


# ==================================================
# ETF评分
# ==================================================
score_df = load_table(
    "dwd_etf_signal"
)

st.subheader("🏆 ETF综合评分")

score_df = score_df.sort_values(
    "signal_score",
    ascending=False
)

st.dataframe(
    score_df,
    use_container_width=True
)

st.divider()


# ==================================================
# 加仓建议
# ==================================================
add_df = load_table(
    "dwd_add_position_signal"
)

st.subheader("💰 加仓建议")

st.dataframe(
    add_df.sort_values(
        "final_score",
        ascending=False
    ),
    use_container_width=True
)

st.divider()


# ==================================================
# 再平衡建议
# ==================================================
rebalance_df = load_table(
    "dwd_rebalance_v2"
)

st.subheader("⚖️ 仓位再平衡")

st.dataframe(
    rebalance_df,
    use_container_width=True
)

st.divider()


# ==================================================
# 风险分析
# ==================================================
risk_df = load_table(
    "dwd_risk_analysis"
)

st.subheader("🚨 风险监控")

st.dataframe(
    risk_df,
    use_container_width=True
)

st.divider()


# ==================================================
# 持仓明细
# ==================================================
position_df = load_table(
    "dwd_floating_profit"
)

st.subheader("📦 当前持仓")

st.dataframe(
    position_df.sort_values(
        "market_value",
        ascending=False
    ),
    use_container_width=True
)

st.success("数据更新时间：" +
           str(position_df["update_time"].max()))