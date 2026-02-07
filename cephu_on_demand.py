import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

TICKER = "NVDA"  # Pas dit aan voor elke aanvraag

def generate_static_analysis(ticker):
    # 1. Data ophalen
    df = yf.download(ticker, period="1y", interval="1d", progress=False)
    if df.empty: return

    # 2. Indicatoren (Bakker methode)
    df['SMA55'] = ta.sma(df['Close'], length=55)
    df['SMA200'] = ta.sma(df['Close'], length=200)
    
    # RSI met StdDev Banden
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['RSI_MA'] = ta.sma(df['RSI'], length=9)
    df['RSI_STD'] = df['RSI'].rolling(9).std()
    df['RSI_Upper'] = df['RSI_MA'] + (1.5 * df['RSI_STD'])
    df['RSI_Lower'] = df['RSI_MA'] - (1.5 * df['RSI_STD'])
    
    # XL DBS Logica
    df['DBS'] = np.where((df['Close'] > df['SMA55']) & (df['RSI'] > 50), 1, 
                         np.where((df['Close'] < df['SMA55']) & (df['RSI'] < 50), -1, 0))

    # 3. Grafiek opbouw
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.07, 
                        row_heights=[0.5, 0.25, 0.25],
                        subplot_titles=(f"{ticker} Price Action", "RSI Momentum (Bakker Style)", "XL DBS Trend Indicator"))

    # Prijs & SMA's
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                                 increasing_line_color='#26A69A', decreasing_line_color='#EF5350', name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA55'], line=dict(color='orange', width=2), name="SMA 55"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA200'], line=dict(color='black', width=2), name="SMA 200"), row=1, col=1)

    # RSI & Clouds
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#7B1FA2', width=1.5)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI_Upper'], line=dict(width=0), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI_Lower'], line=dict(width=0), fill='tonexty', 
                             fillcolor='rgba(128, 128, 128, 0.15)', showlegend=False), row=2, col=1)

    # DBS Bars
    colors_dbs = ['#EF5350' if val == -1 else ('#26A69A' if val == 1 else '#BDBDBD') for val in df['DBS']]
    fig.add_trace(go.Bar(x=df.index, y=df['DBS'], marker_color=colors_dbs), row=3, col=1)

    # 4. Styling (Statische optimalisatie)
    fig.update_layout(
        template="simple_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=60, r=40, t=100, b=60),
        xaxis_rangeslider_visible=False,
        showlegend=False,
        width=1200,
        height=1000,
        font=dict(family="Arial", size=14)
    )

    # Verwijder ballast voor een schone afbeelding
    fig.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True, ticks="")
    fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0", ticks="")

    # OPSLAAN ALS AFBEELDING
    fig.write_image(f"cephu_analysis_{ticker}.png", scale=2) # Scale 2 voor extra scherpte
    print(f"Afbeelding opgeslagen: cephu_analysis_{ticker}.png")

if __name__ == "__main__":
    generate_static_analysis(TICKER)
