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
    page_title="持仓分析",
    page_icon="💼",
    layout="wide"
)

st.title("💼 ETF持仓分析")


# ==================================================
# 数据加载
# ==================================================

@st.cache_data(ttl=60)
def load_position():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            p.etf_code,
            p.etf_name,
            p.quantity,
            p.avg_cost,

            f.current_price,
            f.market_value,
            f.floating_profit,
            f.floating_profit_pct

        FROM dwd_position p

        LEFT JOIN dwd_floating_profit f
               ON p.etf_code=f.etf_code

        ORDER BY f.market_value DESC
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=60)
def load_allocation():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            etf_code,
            etf_name,
            market_value,
            allocation_pct
        FROM dwd_allocation
        ORDER BY allocation_pct DESC
        """,
        conn
    )

    conn.close()

    return df


# ==================================================
# 数据
# ==================================================

position_df = load_position()

allocation_df = load_allocation()


# ==================================================
# 第一部分
# ==================================================

st.subheader("当前持仓")

if not position_df.empty:

    show_df = position_df.copy()

    show_df = show_df.rename(
        columns={
            "etf_code": "代码",
            "etf_name": "ETF名称",
            "quantity": "持仓数量",
            "avg_cost": "持仓成本",
            "current_price": "当前价格",
            "market_value": "市值",
            "floating_profit": "浮动盈亏",
            "floating_profit_pct": "收益率%"
        }
    )

    st.dataframe(
        show_df,
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# 第二部分
# ==================================================

st.subheader("盈利TOP10")

profit_df = position_df.sort_values(
    "floating_profit",
    ascending=False
).head(10)

if not profit_df.empty:

    fig = px.bar(
        profit_df,
        x="etf_name",
        y="floating_profit",
        title="盈利排行TOP10"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ==================================================
# 第三部分
# ==================================================

st.subheader("亏损TOP10")

loss_df = position_df.sort_values(
    "floating_profit",
    ascending=True
).head(10)

if not loss_df.empty:

    fig = px.bar(
        loss_df,
        x="etf_name",
        y="floating_profit",
        title="亏损排行TOP10"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ==================================================
# 第四部分
# ==================================================

st.subheader("仓位占比")

if not allocation_df.empty:

    fig = px.pie(
        allocation_df,
        names="etf_name",
        values="allocation_pct",
        title="ETF仓位占比"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ==================================================
# 第五部分
# ==================================================

st.subheader("持仓明细分析")

if not position_df.empty:

    best = position_df.sort_values(
        "floating_profit_pct",
        ascending=False
    ).iloc[0]

    worst = position_df.sort_values(
        "floating_profit_pct",
        ascending=True
    ).iloc[0]

    largest = allocation_df.iloc[0]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "最佳ETF",
        best["etf_name"],
        f"{best['floating_profit_pct']:.2f}%"
    )

    col2.metric(
        "最弱ETF",
        worst["etf_name"],
        f"{worst['floating_profit_pct']:.2f}%"
    )

    col3.metric(
        "第一重仓",
        largest["etf_name"],
        f"{largest['allocation_pct']:.2f}%"
    )


# ==================================================
# AI分析
# ==================================================

st.subheader("AI持仓点评")

if not position_df.empty:

    summary = []

    total_count = len(position_df)

    summary.append(
        f"当前持仓ETF数量：{total_count}"
    )

    profit_count = len(
        position_df[
            position_df["floating_profit"] > 0
        ]
    )

    summary.append(
        f"盈利ETF数量：{profit_count}"
    )

    summary.append(
        f"最大盈利ETF：{best['etf_name']}"
    )

    summary.append(
        f"最大亏损ETF：{worst['etf_name']}"
    )

    summary.append(
        f"当前第一重仓：{largest['etf_name']}"
    )

    st.success(
        "\n\n".join(summary)
    )


st.caption(
    "数据来源：dwd_position / dwd_floating_profit / dwd_allocation"
)