# -*- coding: utf-8 -*-

import streamlit as st

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from _utils import load_df, rename_columns

st.title("📒 交易复盘")

# ── 交易统计 ──
trade_df = load_df("SELECT * FROM ods_trade_record ORDER BY trade_date DESC")

st.subheader("📊 交易统计")
if not trade_df.empty:
    total = len(trade_df)
    buy_df = trade_df[trade_df["trade_type"] == "买入"]
    sell_df = trade_df[trade_df["trade_type"] == "卖出"]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("总交易次数", total)
    c2.metric("买入次数", len(buy_df))
    c3.metric("卖出次数", len(sell_df))
    c4.metric("累计买入", f"{buy_df['amount'].sum():,.0f}")
    c5.metric("累计卖出", f"{sell_df['amount'].sum():,.0f}")

st.divider()

# ── 交易次数排行 ──
st.subheader("🔥 ETF 交易频次")
if not trade_df.empty:
    freq_df = (trade_df.groupby(["etf_code", "etf_name"]).size()
               .reset_index(name="trade_count")
               .sort_values("trade_count", ascending=False))
    st.dataframe(rename_columns(freq_df.head(20)), use_container_width=True, hide_index=True)

st.divider()

# ── 历史明细 ──
st.subheader("📜 交易明细")
if not trade_df.empty:
    etf_list = ["全部"] + sorted(trade_df["etf_name"].dropna().unique().tolist())
    selected = st.selectbox("ETF 筛选", etf_list)
    show_df = trade_df if selected == "全部" else trade_df[trade_df["etf_name"] == selected]
    st.dataframe(rename_columns(show_df), use_container_width=True, hide_index=True, height=500)
else:
    st.info("暂无交易记录")

st.caption("数据来源：ods_trade_record")