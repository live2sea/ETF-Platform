# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

from pathlib import Path


# ==================================================
# 基础配置
# ==================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

DB_PATH = ROOT_DIR / "data" / "etf.db"

st.set_page_config(
    page_title="总览",
    page_icon="📊",
    layout="wide"
)

st.title("📊 ETF投资总览")


# ==================================================
# 数据加载
# ==================================================

@st.cache_data(ttl=60)
def load_dashboard():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM dwd_dashboard
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=60)
def load_category():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            category_name,
            market_value,
            allocation_pct,
            etf_count,
            risk_level
        FROM dwd_category_allocation
        ORDER BY allocation_pct DESC
        """,
        conn
    )

    conn.close()

    return df


# ==================================================
# 数据准备
# ==================================================

dashboard_df = load_dashboard()

category_df = load_category()

dashboard_map = {}

for _, row in dashboard_df.iterrows():
    dashboard_map[row["item_name"]] = row["item_value"]


# ==================================================
# 第一行 KPI
# ==================================================

st.subheader("账户概览")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "总成本",
    dashboard_map.get("总成本", "--")
)

c2.metric(
    "总市值",
    dashboard_map.get("总市值", "--")
)

c3.metric(
    "总盈亏",
    dashboard_map.get("总盈亏", "--")
)

c4.metric(
    "收益率",
    dashboard_map.get("收益率", "--")
)


# ==================================================
# 第二行 核心指标
# ==================================================

st.subheader("核心指标")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "第一重仓",
    dashboard_map.get("第一重仓", "--")
)

c2.metric(
    "最佳ETF",
    dashboard_map.get("最佳ETF", "--")
)

c3.metric(
    "推荐加仓",
    dashboard_map.get("推荐加仓", "--")
)

c4.metric(
    "高风险项",
    dashboard_map.get("高风险项数量", "--")
)


# ==================================================
# 第三行 图表
# ==================================================

st.subheader("资产配置")

col1, col2 = st.columns([1, 1])

with col1:

    if not category_df.empty:

        fig = px.pie(
            category_df,
            names="category_name",
            values="allocation_pct",
            title="仓位占比"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

with col2:

    if not category_df.empty:

        fig = px.bar(
            category_df,
            x="category_name",
            y="allocation_pct",
            title="各分类仓位占比"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ==================================================
# 第四行 仓位结构
# ==================================================

st.subheader("仓位结构")

show_df = category_df.copy()

show_df = show_df.rename(
    columns={
        "category_name": "分类",
        "market_value": "市值",
        "allocation_pct": "占比(%)",
        "etf_count": "ETF数量",
        "risk_level": "风险等级"
    }
)

st.dataframe(
    show_df,
    use_container_width=True,
    hide_index=True
)


# ==================================================
# 第五行 AI摘要
# ==================================================

st.subheader("AI投资摘要")

summary = []

profit_pct = dashboard_map.get("收益率", "--")

summary.append(
    f"当前账户收益率：{profit_pct}"
)

if not category_df.empty:

    top_category = category_df.iloc[0]

    summary.append(
        f"当前最大仓位：{top_category['category_name']} "
        f"({top_category['allocation_pct']:.2f}%)"
    )

    high_risk_df = category_df[
        category_df["risk_level"] == "高风险"
    ]

    if not high_risk_df.empty:

        summary.append(
            f"高风险分类数量：{len(high_risk_df)}"
        )

best_etf = dashboard_map.get("最佳ETF", "--")

summary.append(
    f"当前最强ETF：{best_etf}"
)

add_etf = dashboard_map.get("推荐加仓", "--")

summary.append(
    f"优先关注：{add_etf}"
)

st.success(

    "\n\n".join(summary)

)


# ==================================================
# 页脚
# ==================================================

st.caption(
    "数据来源：ETF交易分析平台 | 更新频率：run_daily.py"
)