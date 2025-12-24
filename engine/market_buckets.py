def assign_bucket(d):
    rsi = d["rsi"]
    ema9, ema26, ema50 = d["ema9"], d["ema26"], d["ema50"]
    price = d["ltp"]
    vwap = d["vwap"]
    adx = d["adx"]

    if rsi >= 80 and price > vwap and adx >= 25:
        return "Extreme Bought"

    if 70 <= rsi < 80 and price > ema9 and adx >= 20:
        return "Overbought"

    if 55 <= rsi < 70 and ema9 > ema26 > ema50 and price > vwap:
        return "Bullish Trend"

    if 30 < rsi <= 45 and ema9 < ema26 < ema50 and price < vwap:
        return "Bearish Trend"

    if 20 < rsi <= 30:
        return "Oversold"

    if rsi <= 20:
        return "Extreme Sold"

    return "Neutral"
