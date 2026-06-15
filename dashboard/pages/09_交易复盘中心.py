# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
import streamlit as st

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

DB_PATH = ROOT_DIR / "data" / "etf.db"

st.set_page_config(
    page_title="交易复盘中心",
    layout="wide"
)

st.title("📒 交易复盘中心")

# =====================================
# 数据加载
# =====================================

@st.cache_data(ttl=60)
def load_trade():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM ods_trade_record
        ORDER BY trade_date DESC
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=60)
def load_profit():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM dwd_floating_profit
        """,
        conn
    )

    conn.close()

    return df


trade_df = load_trade()

profit_df = load_profit()

# =====================================
# 交易统计
# =====================================

st.subheader("📊 交易统计")

total_trade = len(trade_df)

buy_count = len(
    trade_df[
        trade_df["trade_type"] == "买入"
    ]
)

sell_count = len(
    trade_df[
        trade_df["trade_type"] == "卖出"
    ]
)

buy_amount = (
    trade_df[
        trade_df["trade_type"] == "买入"
    ]["amount"].sum()
)

sell_amount = (
    trade_df[
        trade_df["trade_type"] == "卖出"
    ]["amount"].sum()
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("总交易次数", total_trade)

c2.metric("买入次数", buy_count)

c3.metric("卖出次数", sell_count)

c4.metric(
    "累计买入",
    f"{buy_amount:,.0f}"
)

c5.metric(
    "累计卖出",
    f"{sell_amount:,.0f}"
)

# =====================================
# 盈利TOP10
# =====================================

st.subheader("🏆 盈利TOP10")

profit_top = profit_df.sort_values(
    "floating_profit",
    ascending=False
)

st.dataframe(
    profit_top[
        [
            "etf_code",
            "etf_name",
            "floating_profit",
            "floating_profit_pct"
        ]
    ].head(10),
    use_container_width=True
)

# =====================================
# 亏损TOP10
# =====================================

st.subheader("📉 亏损TOP10")

loss_top = profit_df.sort_values(
    "floating_profit"
)

st.dataframe(
    loss_top[
        [
            "etf_code",
            "etf_name",
            "floating_profit",
            "floating_profit_pct"
        ]
    ].head(10),
    use_container_width=True
)

# =====================================
# ETF交易次数排行
# =====================================

st.subheader("🔥 ETF交易次数排行")

trade_rank = (
    trade_df
    .groupby(
        ["etf_code", "etf_name"]
    )
    .size()
    .reset_index(
        name="trade_count"
    )
    .sort_values(
        "trade_count",
        ascending=False
    )
)

st.dataframe(
    trade_rank.head(20),
    use_container_width=True
)

# =====================================
# 历史交易明细
# =====================================

st.subheader("📜 历史交易记录")

etf_list = ["全部"] + sorted(
    trade_df["etf_name"]
    .dropna()
    .unique()
    .tolist()
)

selected = st.selectbox(
    "ETF筛选",
    etf_list
)

show_df = trade_df.copy()

if selected != "全部":

    show_df = show_df[
        show_df["etf_name"] == selected
    ]

st.dataframe(
    show_df,
    use_container_width=True,
    height=500
)