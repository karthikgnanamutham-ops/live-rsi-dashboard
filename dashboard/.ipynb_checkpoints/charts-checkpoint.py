import plotly.graph_objects as go
from engine.indicators import compute_rsi, compute_vwap

def candle_chart(df):
    vwap = compute_vwap(df)
    fig = go.Figure()

    fig.add_candlestick(
        open=df.open, high=df.high,
        low=df.low, close=df.close
    )
    fig.add_scatter(y=vwap, name="VWAP")

    fig.update_layout(height=350, margin=dict(t=20,b=20))
    return fig

def rsi_chart(close):
    rsi = compute_rsi(close)
    fig = go.Figure()
    fig.add_scatter(y=rsi)
    fig.add_hline(y=70)
    fig.add_hline(y=30)
    fig.update_layout(height=200)
    return fig
