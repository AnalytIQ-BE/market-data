import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# --- CONFIGURATIE ---
TICKER = "NVDA"  # Pas hier de ticker aan voor je aanvraag

def generate_analysis(ticker):
    # 1. Data ophalen (Dagelijks - 1 jaar voor goede SMA200 berekening)
    df = yf.download(ticker, period="1y", interval="1d", progress=False)
    
    # 2. Indicatoren Berekenen
    # SMA's
    df['SMA55'] = ta.sma(df['Close'], length=55)
    df['SMA200'] = ta.sma(df['Close'], length=200)
    
    # VWAP (Op daily chart is dit de 'Anchored' VWAP of Year-to-Date)
    df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])
    
    # RSI met StdDev Banden (Bakker stijl)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['RSI_MA'] = ta.sma(df['RSI'], length=9)
    df['RSI_STD'] = df['RSI'].rolling(9).std()
    df['RSI_Upper'] = df['RSI_MA'] + (1.5 * df['RSI_STD'])
    df['RSI_Lower'] = df['RSI_MA'] - (1.5 * df['RSI_STD'])
    
    # Swing Teller (Simpel: opeenvolgende higher highs / lower lows)
    df['Swing'] = 0
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
            df.loc[df.index[i], 'Swing'] = df['Swing'].iloc[i-1] + 1 if df['Swing'].iloc[i-1] >= 0 else 1
        else:
            df.loc[df.index[i], 'Swing'] = df['Swing'].iloc[i-1] - 1 if df['Swing'].iloc[i-1] <= 0 else -1

    # XL DBS Indicator (Eenvoudige versie: trend & momentum combinatie)
    # Groen als prijs > SMA55 & RSI > 50, Rood als prijs < SMA55 & RSI < 50
    df['DBS'] = np.where((df['Close'] > df['SMA55']) & (df['RSI'] > 50), 1, 
                         np.where((df['Close'] < df['SMA55']) & (df['RSI'] < 50), -1, 0))

    # 3. Grafiek Setup (3 rijen: Prijs, RSI, DBS)
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, 
                        row_heights=[0.6, 0.2, 0.2])

    # --- ROW 1: Candlesticks & SMA/VWAP ---
    # Bakker kleuren: Groen voor stijgend, Rood voor dalend
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                                 increasing_line_color='#26A69A', decreasing_line_color='#EF5350', name="Price"), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA55'], line=dict(color='orange', width=1.5), name="SMA 55"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA200'], line=dict(color='black', width=2), name="SMA 200"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], line=dict(color='blue', width=1, dash='dot'), name="VWAP"), row=1, col=1)

    # Swing Teller Labels
    last_swing = df['Swing'].iloc[-1]
    fig.add_annotation(text=f"Swing: {last_swing}", xref="paper", yref="paper", x=0.02, y=0.95, showarrow=False, font=dict(size=12, color="black"))

    # --- ROW 2: RSI met Banden ---
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=1.5), name="RSI"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI_MA'], line=dict(color='grey', width=1), name="RSI MA"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI_Upper'], line=dict(color='rgba(0,0,0,0)'), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI_Lower'], line=dict(color='rgba(0,0,0,0)'), fill='tonexty', fillcolor='rgba(128, 128, 128, 0.1)', name="StdDev Band"), row=2, col=1)

    # --- ROW 3: XL DBS Indicator ---
    colors_dbs = ['#EF5350' if val == -1 else ('#26A69A' if val == 1 else 'grey') for val in df['DBS']]
    fig.add_trace(go.Bar(x=df.index, y=df['DBS'], marker_color=colors_dbs, name="XL DBS"), row=3, col=1)

    # 4. Layout (Cephu Style)
    fig.update_layout(
        title=f"TECHNICAL ANALYSIS: {ticker}",
        template="simple_white",
        paper_bgcolor="hsl(0, 0, 96)",
        plot_bgcolor="hsl(0, 0, 96)",
        margin=dict(l=50, r=20, t=80, b=50),
        xaxis_rangeslider_visible=False,
        showlegend=False,
        height=900
    )
    
    # Verwijder ticks zoals gevraagd
    fig.update_xaxes(showline=False, ticks="")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)", ticks="")

    fig.write_html(f"analysis_{ticker}.html")
    print(f"Analyse voor {ticker} gegenereerd.")

generate_analysis(TICKER)
