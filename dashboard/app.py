# ================= PATH FIX =================
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

# ================= IMPORTS =================
import streamlit as st
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

from engine.symbols import load_symbols
from engine.indicator_engine import run_indicator_engine
from engine.market_buckets import assign_bucket
from dashboard.charts import candle_chart, rsi_chart

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Trade AI – Market Scanner",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st_autorefresh(interval=90_000, key="auto_refresh")

# ================= SIDEBAR =================
st.sidebar.header("⚙️ Filters")

# ---- PRICE FILTER (TEXT INPUT, CSV LTP) ----
price_min = st.sidebar.text_input("Price Min (LTP)", value="0")
price_max = st.sidebar.text_input("Price Max (LTP)", value="5000")

try:
    price_min = float(price_min)
    price_max = float(price_max)
except:
    st.sidebar.error("Price must be numeric")
    st.stop()

# ---- VOLUME FILTER ----
only_volume_spike = st.sidebar.checkbox(
    "Only Volume Spike Stocks",
    value=True
)

# ================= HEADER =================
st.markdown("## 📊 Trade AI – Market Regime Scanner")
st.caption(
    f"⏱ Last refreshed: {datetime.now().strftime('%d %b %Y, %I:%M:%S %p')}"
)

# ================= LOAD SYMBOLS (CSV LTP FILTER) =================
symbols_df = load_symbols(price_min, price_max)

if symbols_df.empty:
    st.warning("No symbols in this LTP range.")
    st.stop()

st.info(f"📌 Symbols after LTP filter: {len(symbols_df)}")

# ================= RUN INDICATOR ENGINE =================
with st.spinner("🔄 Calculating indicators..."):
    data = run_indicator_engine(symbols_df)

if not data:
    st.warning("No valid data after indicator calculation.")
    st.stop()

# ================= ASSIGN BUCKETS =================
bucket_map = {}
for d in data:
    if only_volume_spike and not d["volume_spike"]:
        continue

    bucket = assign_bucket(d)
    d["bucket"] = bucket
    bucket_map.setdefault(bucket, []).append(d)

# ================= BUCKET DISPLAY ORDER =================
BUCKET_ORDER = [
    "Extreme Bought",
    "Overbought",
    "Bullish Trend",
    "Bearish Trend",
    "Oversold",
    "Extreme Sold",
    "Neutral"
]

# ================= DISPLAY =================
for bucket in BUCKET_ORDER:
    stocks = bucket_map.get(bucket, [])
    if not stocks:
        continue

    st.markdown(f"### 🪣 {bucket} ({len(stocks)})")

    for s in stocks:
        with st.expander(f"{s['company']}  |  LTP ₹{s['ltp']}"):
            st.write(
                f"""
                **RSI:** {s['rsi']}  
                **ADX:** {s['adx']}  
                **VWAP:** {s['vwap']}  
                **EMA 9 / 26 / 50:** {s['ema9']} / {s['ema26']} / {s['ema50']}  
                **MACD:** {s['macd']}  
                **Volume Spike:** {'✅' if s['volume_spike'] else '❌'}
                """
            )

            st.plotly_chart(
                candle_chart(s["ohlc"]),
                use_container_width=True
            )

            st.plotly_chart(
                rsi_chart(s["ohlc"]["close"]),
                use_container_width=True
            )
