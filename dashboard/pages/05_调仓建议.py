# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
import streamlit as st

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DB_PATH = ROOT_DIR / "data" / "etf.db"

st.set_page_config(
    page_title="调仓建议",
    layout="wide"
)

st.title("⚖️ 调仓建议")

conn = sqlite3.connect(DB_PATH)

# ==================================================
# 调仓分析
# ==================================================

rebalance_df = pd.read_sql(
    """
    SELECT *
    FROM dwd_rebalance_v2
    ORDER BY ABS(deviation_pct) DESC
    """,
    conn
)

st.subheader("资产类别偏离情况")

st.dataframe(
    rebalance_df,
    use_container_width=True
)

# ==================================================
# 建议加仓ETF
# ==================================================

add_df = pd.read_sql(
    """
    SELECT
        etf_code,
        etf_name,
        final_score,
        recommend_amount,
        recommendation
    FROM dwd_add_position_signal
    WHERE recommend_amount > 0
    ORDER BY final_score DESC
    """,
    conn
)

st.subheader("建议加仓ETF")

st.dataframe(
    add_df,
    use_container_width=True
)

# ==================================================
# TOP5加仓标的
# ==================================================

st.subheader("TOP5加仓标的")

top5 = add_df.head(5)

cols = st.columns(5)

for i, (_, row) in enumerate(top5.iterrows()):

    cols[i].metric(
        row["etf_name"],
        f"{row['final_score']:.0f}",
        f"建议{row['recommend_amount']:.0f}"
    )

conn.close()