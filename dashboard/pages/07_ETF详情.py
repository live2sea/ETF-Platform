# -*- coding: utf-8 -*-

import streamlit as st
import plotly.graph_objects as go

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from _utils import load_df, rename_columns

st.title("📈 ETF 详情")

# ── 选择器 ──
etf_df = load_df("SELECT etf_code, etf_name FROM dwd_position ORDER BY etf_code")
if etf_df.empty:
    st.warning("暂无持仓数据")
    st.stop()

etf_df["etf_name"] = etf_df["etf_name"].fillna("")
options = (etf_df["etf_code"] + " " + etf_df["etf_name"]).tolist()
selected = st.sidebar.selectbox("选择 ETF", options)
code = selected.split()[0]

# ── 单 ETF 数据加载 ──
pos_row = load_df(
    "SELECT p.quantity, p.avg_cost, f.current_price, "
    "f.floating_profit, f.floating_profit_pct "
    "FROM dwd_position p LEFT JOIN dwd_floating_profit f ON p.etf_code=f.etf_code "
    "WHERE p.etf_code=?", params=[code]
)

kline_df = load_df(
    "SELECT trade_date, close_price FROM ods_market_kline "
    "WHERE etf_code=? ORDER BY trade_date", params=[code]
)

ma_df = load_df(
    "SELECT trade_date, close_price, ma20, ma60, ma120, ma250, trend_score, trend_level, signal "
    "FROM dwd_ma_factor WHERE etf_code=? ORDER BY trade_date", params=[code]
)

rsi_df = load_df(
    "SELECT * FROM dwd_rsi_factor WHERE etf_code=?", params=[code]
)

dd_df = load_df(
    "SELECT * FROM dwd_drawdown_factor WHERE etf_code=?", params=[code]
)

signal_df = load_df(
    "SELECT * FROM dwd_etf_signal WHERE etf_code=?", params=[code]
)

# ── 持仓 KPI ──
if not pos_row.empty:
    r = pos_row.iloc[0]
    st.subheader("持仓信息")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("持仓数量", f"{r['quantity']:,.0f}")
    c2.metric("持仓成本", f"{r['avg_cost']:.3f}")
    c3.metric("当前价格", f"{r['current_price']:.3f}")
    c4.metric("收益率", f"{r['floating_profit_pct']:.2f}%")

# ── 均线图 ──
if not ma_df.empty:
    st.subheader("均线趋势")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ma_df["trade_date"], y=ma_df["close_price"],
                             name="收盘价", line=dict(width=1.5)))
    fig.add_trace(go.Scatter(x=ma_df["trade_date"], y=ma_df["ma20"],
                             name="MA20", line=dict(dash="dot")))
    fig.add_trace(go.Scatter(x=ma_df["trade_date"], y=ma_df["ma60"],
                             name="MA60", line=dict(dash="dot")))
    fig.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

# ── 技术指标行 ──
st.subheader("技术指标")

# MA 指标
if not ma_df.empty:
    last = ma_df.iloc[-1]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("MA20", f"{last['ma20']:.3f}")
    c2.metric("MA60", f"{last['ma60']:.3f}")
    c3.metric("MA120", f"{last['ma120']:.3f}")
    c4.metric("MA250", f"{last['ma250']:.3f}")
    c5.metric("趋势评分", f"{last['trend_score']:.0f}")

# RSI + 回撤
c_a, c_b = st.columns(2)
if not rsi_df.empty:
    r = rsi_df.iloc[-1]
    with c_a:
        st.metric("RSI6", f"{r['rsi6']:.1f}")
        st.metric("RSI12", f"{r['rsi12']:.1f}")
        st.metric("RSI24", f"{r['rsi24']:.1f}")

if not dd_df.empty:
    d = dd_df.iloc[0]
    with c_b:
        st.metric("52周最高", f"{d['high_52w']:.3f}")
        st.metric("当前价格", f"{d['current_price']:.3f}")
        st.metric("回撤幅度", f"{d['drawdown_pct']:.2f}%")

# ── 综合评分 ──
if not signal_df.empty:
    s = signal_df.iloc[0]
    st.subheader("综合评分")
    c1, c2, c3 = st.columns(3)
    c1.metric("综合评分", f"{s['signal_score']:.1f}")
    c2.metric("等级", s["level"])
    c3.metric("建议", s["suggestion"])

# ── 建议 ──
st.subheader("📋 投资参考")
advice = []
if not signal_df.empty:
    score = s["signal_score"]
    if score >= 70:
        advice.append("✅ 综合评分较高，属于优先加仓候选")
    elif score >= 60:
        advice.append("🟡 综合评分中等，建议继续持有观察")
    else:
        advice.append("🔴 综合评分偏弱，暂停新增仓位")

if not rsi_df.empty:
    r6 = r["rsi6"]
    if r6 < 20:
        advice.append("📉 RSI 进入超卖区，关注反弹机会")
    elif r6 > 80:
        advice.append("📈 RSI 进入超买区，注意回调风险")

if not dd_df.empty:
    dd = d["drawdown_pct"]
    if dd <= -30:
        advice.append("💎 深度回撤区，可纳入重点观察名单")

for msg in advice:
    st.info(msg)

st.caption("数据来源：ods_market_kline / dwd_ma_factor / dwd_rsi_factor / dwd_drawdown_factor")