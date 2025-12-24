import requests
import pandas as pd
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DHAN_URL = "https://api.dhan.co/v2/charts/intraday"
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

if not ACCESS_TOKEN:
    raise EnvironmentError("❌ DHAN_ACCESS_TOKEN not found in .env")

def get_ohlc(security_id, interval=5, lookback_days=7):
    """
    Fetch intraday OHLC data from Dhan using rolling date range.
    This guarantees latest available data (pre-market, weekends, holidays).
    """

    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

    payload = {
        "securityId": str(security_id),
        "exchangeSegment": "NSE_EQ",
        "instrument": "EQUITY",
        "interval": interval,
        "fromDate": from_date,
        "toDate": to_date
    }

    headers = {
        "access-token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    try:
        r = requests.post(
            DHAN_URL,
            json=payload,
            headers=headers,
            timeout=10
        )

        if r.status_code != 200:
            return pd.DataFrame()

        d = r.json()

        if not d or "close" not in d:
            return pd.DataFrame()

        df = pd.DataFrame({
            "open": d.get("open", []),
            "high": d.get("high", []),
            "low": d.get("low", []),
            "close": d.get("close", []),
            "volume": d.get("volume", [])
        })

        return df.dropna()

    except Exception:
        return pd.DataFrame()
