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
def load_signal():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM dwd_etf_signal
        ORDER BY signal_score DESC
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


signal_df = load_signal()
add_df = load_add_position()
rebalance_df = load_rebalance()
risk_df = load_risk()

# =====================================
# 账户评分
# =====================================

st.subheader("账户评分")

if not signal_df.empty:

    account_score = round(
        signal_df["signal_score"].mean(),
        1
    )

    if account_score >= 70:
        grade = "A"
    elif account_score >= 60:
        grade = "B"
    elif account_score >= 50:
        grade = "C"
    else:
        grade = "D"

    c1, c2 = st.columns(2)

    c1.metric(
        "账户综合评分",
        account_score
    )

    c2.metric(
        "账户等级",
        grade
    )

# =====================================
# 今日操作建议
# =====================================

st.subheader("今日操作建议")

buy_df = add_df[
    add_df["recommend_amount"] > 0
]

if not buy_df.empty:

    st.success(
        f"今日推荐关注 {len(buy_df)} 只ETF"
    )

    st.dataframe(
        buy_df[
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

# =====================================
# TOP5加仓ETF
# =====================================

st.subheader("TOP5加仓ETF")

top5 = add_df.head(5)

if not top5.empty:

    st.dataframe(
        top5[
            [
                "etf_code",
                "etf_name",
                "final_score",
                "recommend_amount"
            ]
        ],
        use_container_width=True
    )

# =====================================
# 风险警报
# =====================================

st.subheader("风险警报")

high_risk = risk_df[
    risk_df["risk_level"] == "高"
]

if high_risk.empty:

    st.success("暂无高风险项")

else:

    for _, row in high_risk.iterrows():

        st.error(
            f"{row['risk_name']} : "
            f"{row['suggestion']}"
        )

# =====================================
# 调仓建议
# =====================================

st.subheader("调仓建议")

adjust_df = rebalance_df[
    rebalance_df["action"] != "持有"
]

if not adjust_df.empty:

    st.dataframe(
        adjust_df[
            [
                "category",
                "current_pct",
                "target_pct",
                "deviation_pct",
                "suggest_amount",
                "action"
            ]
        ],
        use_container_width=True
    )

# =====================================
# AI总结
# =====================================

st.subheader("AI总结")

summary = []

if not signal_df.empty:

    best = signal_df.iloc[0]

    summary.append(
        f"当前最强ETF："
        f"{best['etf_name']} "
        f"(评分{best['signal_score']:.0f})"
    )

if not add_df.empty:

    best_buy = add_df.iloc[0]

    summary.append(
        f"建议优先加仓："
        f"{best_buy['etf_name']}"
    )

if not rebalance_df.empty:

    biggest = rebalance_df.iloc[0]

    summary.append(
        f"偏离目标仓位最大："
        f"{biggest['category']}"
    )

if high_risk.empty:

    summary.append(
        "当前组合整体风险可控"
    )

else:

    summary.append(
        f"存在 {len(high_risk)} 项高风险指标"
    )

for item in summary:

    st.info(item)