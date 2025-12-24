import pandas as pd

def compute_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def rsi_bucket(rsi):
    if rsi >= 80:
        return "Extreme Bought"
    elif rsi >= 70:
        return "Overbought"
    elif rsi >= 55:
        return "Bullish"
    elif rsi >= 45:
        return "Bearish"
    elif rsi >= 30:
        return "Oversold"
    else:
        return "Extreme Sold"
