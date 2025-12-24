import pandas as pd

def load_symbols(price_min, price_max):
    df = pd.read_csv("stocks.csv")

    # Normalize columns
    df.columns = (
        df.columns.str.strip().str.upper().str.replace(" ", "_")
    )

    # LTP PREFILTER (VERY IMPORTANT)
    df = df[
        (df["LTP"] >= price_min) &
        (df["LTP"] <= price_max)
    ]

    return df[[
        "SYMBOL",
        "NAME_OF_COMPANY",
        "SECURITY_ID",
        "LTP"
    ]]
