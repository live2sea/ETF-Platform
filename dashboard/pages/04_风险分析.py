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
    page_title="风险分析",
    page_icon="⚠️",
    layout="wide"
)

st.title("⚠️ 风险分析中心")


# ==================================================
# 数据加载
# ==================================================

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


@st.cache_data(ttl=60)
def load_health():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(
        """
        SELECT *
        FROM dwd_position_health
        """,
        conn
    )

    conn.close()

    return df


risk_df = load_risk()

health_df = load_health()


# ==================================================
# 第一部分
# ==================================================

st.subheader("账户健康度")

if not health_df.empty:

    show_df = health_df.rename(
        columns={
            "health_item": "指标",
            "item_value": "数值",
            "risk_level": "风险等级",
            "suggestion": "建议"
        }
    )

    st.dataframe(
        show_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("暂无健康度数据")


# ==================================================
# 第二部分
# ==================================================

st.subheader("风险项明细")

if not risk_df.empty:

    show_df = risk_df.rename(
        columns={
            "risk_type": "风险类型",
            "risk_name": "风险名称",
            "risk_value": "风险值",
            "risk_level": "风险等级",
            "suggestion": "建议"
        }
    )

    st.dataframe(
        show_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("暂无风险分析数据")


# ==================================================
# 第三部分
# ==================================================

st.subheader("风险等级分布")

if not risk_df.empty:

    level_df = (
        risk_df
        .groupby("risk_level")
        .size()
        .reset_index(name="count")
    )

    fig = px.pie(
        level_df,
        names="risk_level",
        values="count",
        title="风险等级分布"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ==================================================
# 第四部分
# ==================================================

st.subheader("风险值排名")

if not risk_df.empty:

    fig = px.bar(
        risk_df.sort_values(
            "risk_value",
            ascending=False
        ),
        x="risk_name",
        y="risk_value",
        color="risk_level",
        title="风险值排行"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ==================================================
# 第五部分
# ==================================================

st.subheader("高风险项目")

if not risk_df.empty:

    high_risk = risk_df[
        risk_df["risk_level"].isin(
            ["高风险", "HIGH", "H"]
        )
    ]

    if not high_risk.empty:

        st.warning(
            f"发现 {len(high_risk)} 项高风险内容"
        )

        st.dataframe(
            high_risk,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "当前未发现高风险项目"
        )


# ==================================================
# 第六部分
# ==================================================

st.subheader("AI风险点评")

summary = []

if not risk_df.empty:

    risk_count = len(risk_df)

    summary.append(
        f"当前识别风险项数量：{risk_count}"
    )

    high_count = len(
        risk_df[
            risk_df["risk_level"].isin(
                ["高风险", "HIGH", "H"]
            )
        ]
    )

    summary.append(
        f"高风险项目数量：{high_count}"
    )

    top_risk = risk_df.sort_values(
        "risk_value",
        ascending=False
    ).iloc[0]

    summary.append(
        f"最大风险来源：{top_risk['risk_name']}"
    )

    summary.append(
        f"风险等级：{top_risk['risk_level']}"
    )

    summary.append(
        f"建议：{top_risk['suggestion']}"
    )

    if high_count == 0:

        summary.append(
            "整体风险处于可控范围。"
        )

    elif high_count <= 2:

        summary.append(
            "存在局部风险，建议重点关注。"
        )

    else:

        summary.append(
            "风险偏高，建议逐步优化仓位结构。"
        )

    st.success(
        "\n\n".join(summary)
    )


# ==================================================
# 第七部分
# ==================================================

st.subheader("风险处理建议")

if not risk_df.empty:

    suggestion_df = risk_df[
        [
            "risk_name",
            "risk_level",
            "suggestion"
        ]
    ]

    st.dataframe(
        suggestion_df,
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# 页脚
# ==================================================

st.caption(
    "数据来源：dwd_risk_analysis / dwd_position_health"
)