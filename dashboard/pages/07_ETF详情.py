# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

DB_PATH = "data/etf.db"


# =====================================
# 数据加载
# =====================================

@st.cache_data(ttl=60)
def load_etf_list():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            etf_code,
            etf_name
        FROM dwd_position
        ORDER BY etf_code
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=60)
def load_kline(etf_code):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        f"""
        SELECT
            trade_date,
            close_price
        FROM ods_market_kline
        WHERE etf_code='{etf_code}'
        ORDER BY trade_date
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=60)
def load_ma(etf_code):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        f"""
        SELECT *
        FROM dwd_ma_factor
        WHERE etf_code='{etf_code}'
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=60)
def load_rsi(etf_code):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        f"""
        SELECT *
        FROM dwd_rsi_factor
        WHERE etf_code='{etf_code}'
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=60)
def load_drawdown(etf_code):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        f"""
        SELECT *
        FROM dwd_drawdown_factor
        WHERE etf_code='{etf_code}'
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=60)
def load_signal(etf_code):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        f"""
        SELECT *
        FROM dwd_etf_signal
        WHERE etf_code='{etf_code}'
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=60)
def load_position(etf_code):

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        f"""
        SELECT
            p.etf_code,
            p.etf_name,
            p.quantity,
            p.avg_cost,
            f.current_price,
            f.floating_profit,
            f.floating_profit_pct
        FROM dwd_position p
        LEFT JOIN dwd_floating_profit f
             ON p.etf_code=f.etf_code
        WHERE p.etf_code='{etf_code}'
        """,
        conn
    )

    conn.close()

    return df


# =====================================
# 页面
# =====================================

st.set_page_config(
    page_title="ETF详情分析",
    layout="wide"
)

st.title("📈 ETF详情分析")


etf_df = load_etf_list()

options = (
    etf_df["etf_code"]
    + " "
    + etf_df["etf_name"]
)

selected = st.sidebar.selectbox(
    "选择ETF",
    options
)

etf_code = selected.split()[0]

# =====================================
# 持仓信息
# =====================================

position_df = load_position(etf_code)

if not position_df.empty:

    row = position_df.iloc[0]

    st.subheader("当前持仓")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "持仓数量",
        f"{row['quantity']:,.0f}"
    )

    c2.metric(
        "持仓成本",
        f"{row['avg_cost']:.3f}"
    )

    c3.metric(
        "当前价格",
        f"{row['current_price']:.3f}"
    )

    c4.metric(
        "收益率",
        f"{row['floating_profit_pct']:.2f}%"
    )

# =====================================
# K线图
# =====================================

kline_df = load_kline(etf_code)

if not kline_df.empty:

    st.subheader("价格走势图")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=kline_df["trade_date"],
            y=kline_df["close_price"],
            name="收盘价"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================
# MA指标
# =====================================

ma_df = load_ma(etf_code)

if not ma_df.empty:

    row = ma_df.iloc[0]

    st.subheader("MA趋势")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("MA20", round(row["ma20"], 3))
    c2.metric("MA60", round(row["ma60"], 3))
    c3.metric("MA120", round(row["ma120"], 3))
    c4.metric("MA250", round(row["ma250"], 3))
    c5.metric("趋势评分", row["trend_score"])

# =====================================
# RSI
# =====================================

rsi_df = load_rsi(etf_code)

if not rsi_df.empty:

    row = rsi_df.iloc[0]

    st.subheader("RSI指标")

    c1, c2, c3 = st.columns(3)

    c1.metric("RSI6", round(row["rsi6"], 2))
    c2.metric("RSI12", round(row["rsi12"], 2))
    c3.metric("RSI24", round(row["rsi24"], 2))

# =====================================
# 回撤
# =====================================

dd_df = load_drawdown(etf_code)

if not dd_df.empty:

    row = dd_df.iloc[0]

    st.subheader("52周回撤")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "52周最高",
        round(row["high_52w"], 3)
    )

    c2.metric(
        "当前价格",
        round(row["current_price"], 3)
    )

    c3.metric(
        "回撤",
        f"{row['drawdown_pct']:.2f}%"
    )

# =====================================
# 综合评分
# =====================================

signal_df = load_signal(etf_code)

if not signal_df.empty:

    row = signal_df.iloc[0]

    st.subheader("综合评分")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "综合评分",
        round(row["signal_score"], 1)
    )

    c2.metric(
        "等级",
        row["level"]
    )

    c3.metric(
        "建议",
        row["suggestion"]
    )

# =====================================
# AI建议
# =====================================

st.subheader("AI投资建议")

advice = []

if not signal_df.empty:

    score = row["signal_score"]

    if score >= 70:
        advice.append("趋势较强，可继续分批加仓。")

    elif score >= 60:
        advice.append("趋势中性，可继续持有观察。")

    else:
        advice.append("趋势偏弱，暂不建议大幅加仓。")

if not rsi_df.empty:

    rsi6 = rsi_df.iloc[0]["rsi6"]

    if rsi6 < 20:
        advice.append("RSI进入超卖区域，关注反弹机会。")

if not dd_df.empty:

    drawdown = dd_df.iloc[0]["drawdown_pct"]

    if drawdown <= -30:
        advice.append("距离52周高点回撤超过30%，处于价值区间。")

for item in advice:
    st.info(item)