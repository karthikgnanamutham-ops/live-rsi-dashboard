from datetime import datetime, timedelta
import pandas as pd

# NSE trading days (Mon–Fri, excluding holidays)
def last_trading_day():
    today = datetime.now().date()

    # If today is Sat (5) or Sun (6), move back
    if today.weekday() == 5:      # Saturday
        today -= timedelta(days=1)
    elif today.weekday() == 6:    # Sunday
        today -= timedelta(days=2)

    # Optional: NSE holiday list (recommended)
    try:
        holidays = pd.read_csv("nse_holidays.csv")["date"]
        holidays = pd.to_datetime(holidays).dt.date.tolist()
    except Exception:
        holidays = []

    # Roll back if holiday
    while today in holidays:
        today -= timedelta(days=1)

    return today.strftime("%Y-%m-%d")
