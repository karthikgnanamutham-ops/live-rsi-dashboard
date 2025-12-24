from concurrent.futures import ThreadPoolExecutor, as_completed
from engine.data_fetcher import get_ohlc
from engine.indicators import (
    compute_rsi, compute_vwap, compute_macd,
    compute_ema, compute_adx, compute_supertrend,
    volume_spike
)

def process_symbol(row):
    ohlc = get_ohlc(row.SECURITY_ID)
    if ohlc.empty or len(ohlc) < 30:
        return None

    close = ohlc["close"]

    ema9 = compute_ema(close, 9).iloc[-1]
    ema26 = compute_ema(close, 26).iloc[-1]
    ema50 = compute_ema(close, 50).iloc[-1]

    rsi = compute_rsi(close).iloc[-1]
    vwap = compute_vwap(ohlc).iloc[-1]
    macd, signal = compute_macd(close)
    adx = compute_adx(ohlc).iloc[-1]
    st = compute_supertrend(ohlc).iloc[-1]

    vol_spike = volume_spike(ohlc["volume"])

    return {
        "company": row.NAME_OF_COMPANY,
        "symbol": row.SYMBOL,
        "ltp": row.LTP,
        "rsi": round(rsi, 1),
        "ema9": round(ema9, 2),
        "ema26": round(ema26, 2),
        "ema50": round(ema50, 2),
        "vwap": round(vwap, 2),
        "macd": round(macd.iloc[-1], 2),
        "adx": round(adx, 1),
        "supertrend": st,
        "volume_spike": vol_spike,
        "ohlc": ohlc
    }


def run_indicator_engine(symbols_df, workers=10):
    results = []

    with ThreadPoolExecutor(workers) as exe:
        futures = [
            exe.submit(process_symbol, row)
            for row in symbols_df.itertuples(index=False)
        ]

        for f in as_completed(futures):
            r = f.result()
            if r:
                results.append(r)

    return results
