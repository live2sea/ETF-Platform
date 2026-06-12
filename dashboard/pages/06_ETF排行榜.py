# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

from pathlib import Path

# ==================================================
# 配置
# ==================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

DB_PATH = ROOT_DIR / "data" / "etf.db"

st.set_page_config(
    page_title="ETF排行榜",
    page_icon="🏆",
    layout="wide"
)

st.title("🏆 ETF排行榜")

# ==================================================
# 数据加载
# ==================================================

@st.cache_data(ttl=60)
def load_signal():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            etf_code,
            etf_name,
            signal_score,
            level,
            suggestion
        FROM dwd_etf_signal
        ORDER BY signal_score DESC
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=60)
def load_ma():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            etf_code,
            etf_name,
            trend_score,
            trend_level,
            signal
        FROM dwd_ma_factor
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=60)
def load_rsi():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            etf_code,
            etf_name,
            rsi6,
            score,
            signal
        FROM dwd_rsi_factor
        ORDER BY rsi6 ASC
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=60)
def load_drawdown():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT
            etf_code,
            etf_name,
            drawdown_pct,
            score,
            signal
        FROM dwd_drawdown_factor
        ORDER BY drawdown_pct ASC
        """,
        conn
    )

    conn.close()

    return df


signal_df = load_signal()
ma_df = load_ma()
rsi_df = load_rsi()
drawdown_df = load_drawdown()

# ==================================================
# 综合评分榜
# ==================================================

st.subheader("🏆 综合评分榜")

st.dataframe(
    signal_df,
    use_container_width=True,
    hide_index=True
)

# ==================================================
# TOP3
# ==================================================

if not signal_df.empty:

    st.subheader("🥇 TOP3 ETF")

    top3 = signal_df.head(3)

    cols = st.columns(3)

    for i, (_, row) in enumerate(top3.iterrows()):

        cols[i].metric(
            row["etf_name"],
            f"{row['signal_score']:.0f}分",
            row["level"]
        )

# ==================================================
# MA趋势榜
# ==================================================

st.subheader("📈 MA趋势榜")

ma_show = ma_df.sort_values(
    "trend_score",
    ascending=False
)

st.dataframe(
    ma_show[
        [
            "etf_name",
            "trend_score",
            "trend_level",
            "signal"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

# ==================================================
# RSI超卖榜
# ==================================================

st.subheader("📉 RSI超卖榜")

rsi_show = rsi_df.sort_values(
    "rsi6",
    ascending=True
)

st.dataframe(
    rsi_show[
        [
            "etf_name",
            "rsi6",
            "score",
            "signal"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

# ==================================================
# 回撤价值榜
# ==================================================

st.subheader("💎 回撤价值榜")

dd_show = drawdown_df.sort_values(
    "drawdown_pct"
)

st.dataframe(
    dd_show[
        [
            "etf_name",
            "drawdown_pct",
            "score",
            "signal"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

# ==================================================
# 综合评分图
# ==================================================

st.subheader("📊 综合评分可视化")

fig = px.bar(
    signal_df.head(15),
    x="etf_name",
    y="signal_score",
    color="level",
    title="ETF综合评分TOP15"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ==================================================
# AI选基建议
# ==================================================

st.subheader("🤖 AI选基建议")

if not signal_df.empty:

    best = signal_df.iloc[0]

    worst = signal_df.iloc[-1]

    summary = f"""
当前评分最高ETF：

{best['etf_name']}

综合评分：{best['signal_score']:.0f}

评级：{best['level']}

建议：{best['suggestion']}

--------------------------------------

当前评分最低ETF：

{worst['etf_name']}

综合评分：{worst['signal_score']:.0f}

评级：{worst['level']}

建议：{worst['suggestion']}

--------------------------------------

优先关注：

1. 综合评分高于70

2. RSI低于20

3. 回撤超过25%

同时满足上述条件的ETF
通常具备较好的中长期配置价值。
"""

    st.success(summary)

# ==================================================
# 页脚
# ==================================================

st.caption(
    "数据来源：dwd_etf_signal / dwd_ma_factor / dwd_rsi_factor / dwd_drawdown_factor"
)