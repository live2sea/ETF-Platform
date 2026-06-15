# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
import streamlit as st

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

DB_PATH = ROOT_DIR / "data" / "etf.db"

st.set_page_config(
    page_title="AI投资决策中心",
    layout="wide"
)

st.title("🤖 AI投资决策中心")


# =====================================
# 数据加载
# =====================================

@st.cache_data(ttl=60)
def load_review():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM dwd_daily_review
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=60)
def load_add_position():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM dwd_add_position_signal
        ORDER BY final_score DESC
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=60)
def load_rebalance():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM dwd_rebalance_v2
        ORDER BY ABS(deviation_pct) DESC
        """,
        conn
    )

    conn.close()

    return df


@st.cache_data(ttl=60)
def load_risk():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM dwd_risk_analysis
        """,
        conn
    )

    conn.close()

    return df


review_df = load_review()
add_df = load_add_position()
rebalance_df = load_rebalance()
risk_df = load_risk()

# =====================================
# AI总结
# =====================================

st.subheader("🧠 今日AI结论")

summary_row = review_df[
    review_df["review_item"] == "AI总结"
]

if not summary_row.empty:

    st.success(
        summary_row.iloc[0]["review_value"]
    )

# =====================================
# 今日复盘
# =====================================

st.subheader("📋 今日复盘")

c1, c2, c3, c4 = st.columns(4)

try:

    total_asset = review_df[
        review_df["review_item"] == "总资产"
    ].iloc[0]["review_value"]

    total_profit = review_df[
        review_df["review_item"] == "总盈亏"
    ].iloc[0]["review_value"]

    profit_pct = review_df[
        review_df["review_item"] == "收益率"
    ].iloc[0]["review_value"]

    best_etf = review_df[
        review_df["review_item"] == "最佳ETF"
    ].iloc[0]["review_value"]

    c1.metric(
        "总资产",
        total_asset
    )

    c2.metric(
        "总盈亏",
        total_profit
    )

    c3.metric(
        "收益率",
        profit_pct
    )

    c4.metric(
        "最佳ETF",
        best_etf
    )

except:
    st.warning("暂无复盘数据")

# =====================================
# 推荐加仓
# =====================================

st.subheader("💰 推荐加仓")

add_show = add_df[
    add_df["recommend_amount"] > 0
].copy()

if not add_show.empty:

    st.dataframe(
        add_show[
            [
                "etf_code",
                "etf_name",
                "final_score",
                "recommend_amount",
                "recommendation"
            ]
        ],
        use_container_width=True
    )

else:

    st.info("当前无推荐加仓ETF")

# =====================================
# 调仓建议
# =====================================

st.subheader("⚖️ 调仓建议")

if not rebalance_df.empty:

    st.dataframe(
        rebalance_df[
            [
                "category",
                "current_pct",
                "target_pct",
                "deviation_pct",
                "action",
                "suggest_amount"
            ]
        ],
        use_container_width=True
    )

# =====================================
# 风险预警
# =====================================

st.subheader("🚨 风险预警")

high_risk = risk_df[
    risk_df["risk_level"].isin(
        ["高", "HIGH"]
    )
]

if high_risk.empty:

    st.success(
        "当前无高风险项"
    )

else:

    st.dataframe(
        high_risk,
        use_container_width=True
    )

# =====================================
# 综合建议
# =====================================

st.subheader("🎯 综合投资建议")

if not add_show.empty:

    top_etf = add_show.iloc[0]

    st.info(
        f"""
优先关注：

{top_etf['etf_code']} {top_etf['etf_name']}

推荐金额：

{top_etf['recommend_amount']:,.0f} 元

综合评分：

{top_etf['final_score']}
"""
    )

else:

    st.info(
        "暂无明确加仓目标"
    )