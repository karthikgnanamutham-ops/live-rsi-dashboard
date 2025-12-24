from concurrent.futures import ThreadPoolExecutor, as_completed
from config import PRICE_MIN, PRICE_MAX, MAX_WORKERS
from engine.data_fetcher import get_ohlc
from engine.indicators import compute_rsi, compute_vwap, volume_spike


# =========================
# Scan ONE symbol
# =========================
def scan_one(row):
    """
    row -> namedtuple from itertuples(index=False)
    """
    try:
        security_id = row.SECURITY_ID
        symbol = row.SYMBOL
        company = row.NAME_OF_COMPANY

        ohlc = get_ohlc(security_id)

        if ohlc.empty or len(ohlc) < 30:
            return None

        close = ohlc["close"]
        price = float(close.iloc[-1])

        # Price filter (temporarily relaxed)
        if not (PRICE_MIN <= price <= PRICE_MAX):
            return None

        rsi = compute_rsi(close).iloc[-1]
        vwap = compute_vwap(ohlc).iloc[-1]
        spike = volume_spike(ohlc["volume"])

        bias = "BUY" if price > vwap else "SELL"
        confidence = "A" if spike and abs(rsi - 50) > 20 else "B"

        return {
            "company": company,
            "symbol": symbol,
            "price": round(price, 2),
            "rsi": round(float(rsi), 1),
            "bias": bias,
            "confidence": confidence,
            "ohlc": ohlc
        }

    except Exception as e:
        print(f"[ERROR] {row.SYMBOL} → {e}")
        return None


# =========================
# Scan ALL symbols
# =========================
def generate_signals(
    symbols_df,
    price_min=0,
    price_max=1e9,
    min_volume=0,
    require_volume_spike=False
):
    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(scan_one, row)
            for row in symbols_df.itertuples(index=False)
        ]

        for f in as_completed(futures):
            r = f.result()
            if not r:
                continue

            # ---- PRICE FILTER ----
            if not (price_min <= r["price"] <= price_max):
                continue

            # ---- VOLUME FILTER ----
            last_vol = r["ohlc"]["volume"].iloc[-1]
            if last_vol < min_volume:
                continue

            if require_volume_spike and r["confidence"] != "A":
                continue

            results.append(r)

    return results

