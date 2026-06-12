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
    page_title="ETF评分",
    page_icon="🏆",
    layout="wide"
)

st.title("🏆 ETF综合评分")


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
            ma_score,
            rsi_score,
            drawdown_score,
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


signal_df = load_signal()

if signal_df.empty:

    st.warning("暂无评分数据")

    st.stop()


# ==================================================
# 第一部分
# ==================================================

st.subheader("ETF评分排行榜")

show_df = signal_df.rename(
    columns={
        "etf_code": "代码",
        "etf_name": "ETF名称",
        "ma_score": "MA评分",
        "rsi_score": "RSI评分",
        "drawdown_score": "回撤评分",
        "signal_score": "综合评分",
        "level": "等级",
        "suggestion": "建议"
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

st.subheader("TOP ETF")

top3 = signal_df.head(3)

c1, c2, c3 = st.columns(3)

if len(top3) >= 1:

    c1.metric(
        "🥇 第一名",
        top3.iloc[0]["etf_name"],
        f"{top3.iloc[0]['signal_score']:.0f}分"
    )

if len(top3) >= 2:

    c2.metric(
        "🥈 第二名",
        top3.iloc[1]["etf_name"],
        f"{top3.iloc[1]['signal_score']:.0f}分"
    )

if len(top3) >= 3:

    c3.metric(
        "🥉 第三名",
        top3.iloc[2]["etf_name"],
        f"{top3.iloc[2]['signal_score']:.0f}分"
    )


# ==================================================
# 第三部分
# ==================================================

st.subheader("综合评分排名")

fig = px.bar(
    signal_df.head(15),
    x="etf_name",
    y="signal_score",
    color="level",
    title="ETF综合评分"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==================================================
# 第四部分
# ==================================================

st.subheader("等级分布")

level_df = (
    signal_df
    .groupby("level")
    .size()
    .reset_index(name="count")
)

fig = px.pie(
    level_df,
    names="level",
    values="count",
    title="评级分布"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==================================================
# 第五部分
# ==================================================

st.subheader("评分拆解")

selected_etf = st.selectbox(
    "选择ETF",
    signal_df["etf_name"]
)

detail = signal_df[
    signal_df["etf_name"] == selected_etf
].iloc[0]

score_df = pd.DataFrame({

    "指标": [
        "MA趋势",
        "RSI位置",
        "回撤空间"
    ],

    "评分": [
        detail["ma_score"],
        detail["rsi_score"],
        detail["drawdown_score"]
    ]

})

fig = px.bar(
    score_df,
    x="指标",
    y="评分",
    title=f"{selected_etf} 评分拆解"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==================================================
# 第六部分
# ==================================================

st.subheader("AI点评")

best = signal_df.iloc[0]

worst = signal_df.iloc[-1]

summary = f"""
当前评分最高ETF：

{best['etf_name']}

综合评分：{best['signal_score']:.0f}

评级：{best['level']}

建议：{best['suggestion']}


--------------------------------


当前评分最低ETF：

{worst['etf_name']}

综合评分：{worst['signal_score']:.0f}

评级：{worst['level']}

建议：{worst['suggestion']}


--------------------------------


当前评分体系：

MA趋势 + RSI位置 + 回撤空间

综合形成ETF投资优先级排序。
"""

st.success(summary)


# ==================================================
# 第七部分
# ==================================================

st.subheader("重点关注名单")

focus_df = signal_df[
    signal_df["signal_score"] >= 70
]

if not focus_df.empty:

    st.dataframe(
        focus_df[
            [
                "etf_code",
                "etf_name",
                "signal_score",
                "level",
                "suggestion"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("当前无重点关注ETF")


# ==================================================
# 页脚
# ==================================================

st.caption(
    "数据来源：dwd_etf_signal"
)