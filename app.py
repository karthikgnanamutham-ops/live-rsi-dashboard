import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from streamlit_autorefresh import st_autorefresh

from data_fetcher import get_ohlc
from rsi_engine import compute_rsi, rsi_bucket
from config import MAX_WORKERS, MIN_CANDLES

# =================================================
# PAGE + MOBILE CSS
# =================================================
st.set_page_config(page_title="Live RSI Dashboard", layout="wide")

st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
}
table {
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 LIVE RSI DASHBOARD")

# =================================================
# SIDEBAR – FILTERS & REFRESH
# =================================================
st.sidebar.header("🔹 Filter Set 1 (Left)")

fs1_price_min = st.sidebar.number_input("Set 1 Min Price", 1, 100000, 100)
fs1_price_max = st.sidebar.number_input("Set 1 Max Price", 1, 100000, 500)
fs1_vol = st.sidebar.number_input("Set 1 Min Volume", 0, 10_000_000, 10_000, step=5_000)

st.sidebar.markdown("---")
st.sidebar.header("🔸 Filter Set 2 (Right)")

fs2_price_min = st.sidebar.number_input("Set 2 Min Price", 1, 100000, 500)
fs2_price_max = st.sidebar.number_input("Set 2 Max Price", 1, 100000, 2000)
fs2_vol = st.sidebar.number_input("Set 2 Min Volume", 0, 10_000_000, 50_000, step=10_000)

st.sidebar.markdown("---")

top_n = st.sidebar.selectbox("Top N per bucket", [3, 5, 10, 20], index=1)

refresh_seconds = st.sidebar.number_input(
    "Auto Refresh (seconds)",
    min_value=2,
    max_value=300,
    value=75,
    step=1
)

manual_refresh = st.sidebar.button("🔄 Manual Refresh")
if manual_refresh:
    st.rerun()

clear_cache = st.sidebar.button("🧹 Clear Cache")

if clear_cache:
    st.cache_data.clear()
    st.session_state.clear()
    st.success("Cache cleared. Reloading...")
    st.rerun()

# =================================================
# AUTO REFRESH (DYNAMIC)
# =================================================
st_autorefresh(
    interval=refresh_seconds * 1000,
    key="auto_refresh_dynamic"
)

# =================================================
# NIFTY DIRECTION
# =================================================
NIFTY_SECURITY_ID = "26000"  # verify once
nifty_df = get_ohlc(NIFTY_SECURITY_ID, interval=5)
nifty_direction = "NA"

if not nifty_df.empty and len(nifty_df) >= 20:
    nifty_rsi = compute_rsi(nifty_df["close"]).iloc[-1]
    if nifty_rsi > 55:
        nifty_direction = "🟢 Bullish"
    elif nifty_rsi < 45:
        nifty_direction = "🔴 Bearish"
    else:
        nifty_direction = "🟡 Neutral"

st.subheader(f"📈 NIFTY Direction: {nifty_direction}")

# =================================================
# LOAD STOCK MASTER
# =================================================
stocks = pd.read_csv("stocks.csv").head(300)

# =================================================
# RSI LOGIC
# =================================================
def detect_rsi_cross(prev, now):
    if prev < 30 and now >= 30:
        return "⬆️ Above 30"
    if prev < 50 and now >= 50:
        return "⬆️ Above 50"
    if prev > 70 and now <= 70:
        return "⬇️ Below 70"
    if prev > 50 and now <= 50:
        return "⬇️ Below 50"
    return "—"

def process_stock(row):
    df = get_ohlc(row["security_id"], interval=5)
    if df.empty or len(df) < MIN_CANDLES:
        return None

    df = df.tail(30)
    rsi_series = compute_rsi(df["close"])

    return {
        "Company": row["NAME OF COMPANY"],
        "Price": float(row["LTP"]),
        "RSI": round(float(rsi_series.iloc[-1]), 2),
        "Volume": int(df["volume"].iloc[-1]),
        "RSI Signal": detect_rsi_cross(
            float(rsi_series.iloc[-2]),
            float(rsi_series.iloc[-1])
        ),
        "Bucket": rsi_bucket(float(rsi_series.iloc[-1]))
    }

# =================================================
# EXECUTION (SINGLE SCAN)
# =================================================
start = time.time()
results = []

progress = st.progress(0)
total = len(stocks)

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(process_stock, row) for _, row in stocks.iterrows()]
    for i, f in enumerate(as_completed(futures)):
        r = f.result()
        if r:
            results.append(r)
        progress.progress((i + 1) / total)

elapsed = round(time.time() - start, 2)
df = pd.DataFrame(results)

# =================================================
# HEADER METRICS
# =================================================
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("⏱ Last Refresh", datetime.now().strftime("%H:%M:%S"))
with c2:
    st.metric("🔁 Next Refresh",
              (datetime.now() + timedelta(seconds=refresh_seconds)).strftime("%H:%M:%S"))
with c3:
    st.metric("⚡ Refresh Time (sec)", elapsed)
with c4:
    st.metric("📊 Stocks Scanned", len(stocks))

if df.empty:
    st.warning("No valid data returned.")
    st.stop()

# =================================================
# APPLY FILTER SETS
# =================================================
df_set1 = df[
    (df["Price"] >= fs1_price_min) &
    (df["Price"] <= fs1_price_max) &
    (df["Volume"] >= fs1_vol)
]

df_set2 = df[
    (df["Price"] >= fs2_price_min) &
    (df["Price"] <= fs2_price_max) &
    (df["Volume"] >= fs2_vol)
]

# =================================================
# COLOR STYLING
# =================================================
bucket_colors = {
    "Extreme Bought": "#ffcccc",
    "Overbought": "#ffe0b3",
    "Bullish": "#d6f5d6",
    "Bearish": "#d6e6ff",
    "Oversold": "#ebd6ff",
    "Extreme Sold": "#e0e0e0"
}

def style_bucket(row):
    styles = []
    color = bucket_colors.get(row.get("Bucket"), "")
    for col in row.index:
        cell = f"background-color: {color};"
        if col == "RSI Signal" and row[col] != "—":
            cell += "font-weight: bold;"
        styles.append(cell)
    return styles

bucket_order = [
    "Extreme Bought", "Overbought", "Bullish",
    "Bearish", "Oversold", "Extreme Sold"
]

# =================================================
# RENDER SECTIONS (AUTO-COLLAPSE EMPTY)
# =================================================
def render_section(container, title, df_view):
    with container:
        st.subheader(title)

        for bucket in bucket_order:
            bucket_df = (
                df_view[df_view["Bucket"] == bucket]
                .sort_values("Volume", ascending=False)
                .head(top_n)
            )

            # Auto-collapse empty buckets
            if bucket_df.empty:
                continue

            # Bucket header (acts as color context)
            st.markdown(f"### {bucket}")

            # FINAL DISPLAY DATAFRAME
            display_df = bucket_df[[
                "Company", "Price", "RSI", "Volume", "RSI Signal"
            ]].copy()

            # 🔢 ROUND VALUES
            display_df["Price"] = display_df["Price"].round(0).astype(int)
            display_df["RSI"] = display_df["RSI"].round(0).astype(int)
            display_df["Volume"] = display_df["Volume"].round(0).astype(int)

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

# =================================================
# SIDE-BY-SIDE DISPLAY
# =================================================
left, right = st.columns(2)
render_section(left, "🔹 Filter Set 1 Results", df_set1)
render_section(right, "🔸 Filter Set 2 Results", df_set2)

st.caption("RSI-only scanner • Dual dynamic filters • Color-coded buckets • Dhan API")
