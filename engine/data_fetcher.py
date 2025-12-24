import requests, os, pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from engine.market_calendar import last_trading_day

load_dotenv()

URL = "https://api.dhan.co/v2/charts/intraday"
TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

def get_ohlc(security_id, interval=5):
    trade_date = last_trading_day()

    payload = {
        "securityId": str(security_id),
        "exchangeSegment": "NSE_EQ",
        "instrument": "EQUITY",
        "interval": interval,
        "fromDate": trade_date,
        "toDate": trade_date
    }

    r = requests.post(URL, json=payload, headers={"access-token": TOKEN})

    if r.status_code != 200:
        return pd.DataFrame()

    d = r.json()

    if not d or "close" not in d:
        return pd.DataFrame()

    return pd.DataFrame({
        "open": d["open"],
        "high": d["high"],
        "low": d["low"],
        "close": d["close"],
        "volume": d["volume"]
    })
