import pandas as pd
import numpy as np

# =========================================================
# EMA
# =========================================================
def compute_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


# =========================================================
# RSI (14)
# =========================================================
def compute_rsi(close, period=14):
    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


# =========================================================
# VWAP
# =========================================================
def compute_vwap(df):
    tp = (df["high"] + df["low"] + df["close"]) / 3
    vwap = (tp * df["volume"]).cumsum() / df["volume"].cumsum()
    return vwap


# =========================================================
# MACD (12, 26, 9)
# =========================================================
def compute_macd(close, fast=12, slow=26, signal=9):
    ema_fast = compute_ema(close, fast)
    ema_slow = compute_ema(close, slow)

    macd_line = ema_fast - ema_slow
    signal_line = compute_ema(macd_line, signal)

    return macd_line, signal_line


# =========================================================
# ADX (+DI, -DI)
# =========================================================
def compute_adx(df, period=14):
    high = df["high"]
    low = df["low"]
    close = df["close"]

    plus_dm = high.diff()
    minus_dm = low.diff() * -1

    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()

    plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(period).mean() / atr)

    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    adx = dx.rolling(period).mean()

    return adx


# =========================================================
# SUPERTREND
# =========================================================
def compute_supertrend(df, period=10, multiplier=3):
    high = df["high"]
    low = df["low"]
    close = df["close"]

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()

    hl2 = (high + low) / 2
    upperband = hl2 + multiplier * atr
    lowerband = hl2 - multiplier * atr

    supertrend = pd.Series(index=df.index, dtype=float)
    direction = True  # True = Bullish, False = Bearish

    for i in range(len(df)):
        if i == 0:
            supertrend.iloc[i] = upperband.iloc[i]
            continue

        if close.iloc[i] > supertrend.iloc[i - 1]:
            direction = True
        elif close.iloc[i] < supertrend.iloc[i - 1]:
            direction = False

        supertrend.iloc[i] = (
            lowerband.iloc[i] if direction else upperband.iloc[i]
        )

    return supertrend


# =========================================================
# VOLUME SPIKE (last 5 candles, ANY spike)
# =========================================================
def volume_spike(volume, lookback=5, multiplier=1.2):
    if len(volume) < lookback + 5:
        return False

    recent = volume.iloc[-lookback:]
    baseline = volume.iloc[-(lookback + 5):-lookback].mean()

    return any(recent > baseline * multiplier)
