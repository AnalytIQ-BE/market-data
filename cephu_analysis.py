import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timezone, timedelta

# --- CONFIGURATIE ---
TICKER_FUT = "ES=F"  
TICKER_CASH = "^GSPC" # S&P 500 Index

def generate_clean_basis_chart_html():
    # 1. Data ophalen (period op 1y voor de MA-berekening, tail voor de zoom)
    df_fut = yf.download(TICKER_FUT, period="1y", interval="1d", progress=False)
    df_cash = yf.download(TICKER_CASH, period="1y", interval="1d", progress=False)
    
    if isinstance(df_fut.columns, pd.MultiIndex):
        df_fut.columns = df_fut.columns.get_level_values(0)
    if isinstance(df_cash.columns, pd.MultiIndex):
        df_cash.columns = df_cash.columns.get_level_values(0)

    # 2. Synchroniseren en Berekenen
    df = pd.DataFrame(index=df_fut.index)
    df['ES'] = df_fut['Close']
    df['SPX'] = df_cash['Close']
    df['Basis'] = df['ES'] - df['SPX']
    df['Basis_Avg'] = df['Basis'].rolling(20).mean()

    # Zoom (35 dagen voor web-overzicht)
    df_zoom = df.tail(35)
    y_min = min(df_zoom['ES'].min(), df_zoom['SPX'].min()) * 0.99
    y_max = max(df_zoom['ES'].max(), df_zoom['SPX'].max()) * 1.01

    # 3. Grafiek Setup (De Cephu Master Layout)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, 
                        row_heights=[0.7, 0.3])

    # --- ROW 1: DE TWEE LIJNEN (CASH vs FUTURES) ---
    fig.add_trace(go.Scatter(x=df_zoom.index, y=df_zoom['ES'], 
                             line=dict(color='#26a69a', width=3), 
                             name="ES Futures (Contract)"), row=1, col=1)
    
    fig.add_trace(go.Scatter(x=df_zoom.index, y=df_zoom['SPX'], 
                             line=dict(color='#ef5350', width=2, dash='dot'), 
                             name="SPX Index (Cash Market)"), row=1, col=1)

    # --- ROW 2: DE BASIS SPREAD (HET VERSCHIL) ---
    fig.add_trace(go.Bar(x=df_zoom.index, y=df_zoom['Basis'], 
                         marker_color='#7B1FA2', opacity=0.5,
                         name="Basis Spread"), row=2, col=1)
    
    fig.add_trace(go.Scatter(x=df_zoom.index, y=df_zoom['Basis_Avg'], 
                             line=dict(color='#333333', width=1.5), 
                             name="Average Basis"), row=2, col=1)

    # --- STYLING & CLEANUP ---
    fig.update_layout(
        template="simple_white", 
        paper_bgcolor="#f5f5f5", # Nu met correcte hex hashtag
        plot_bgcolor="#f5f5f5", 
        autosize=True, showlegend=False,
        margin=dict(l=10, r=10, t=100, b=40) # Meer ruimte rechts voor de labels
    )
    # Voeg dit toe om de grafiekhoogte op mobiel/desktop te regelen via de export
    config = {'responsive': True}

    fig.update_xaxes(showticklabels=False, ticks="", showline=False, row=1, col=1)
    fig.update_xaxes(showticklabels=True, ticks="", linecolor='rgba(0,0,0,0.1)', 
                     tickformat="%d %b\n%Y", row=2, col=1)

    fig.update_yaxes(side="right", gridcolor="rgba(0,0,0,0.03)", ticks="", showline=False)
    fig.update_yaxes(range=[y_min, y_max], row=1, col=1)

    # --- DYNAMISCHE LABELS AAN DE RECHTERKANT ---
    last_es = df_zoom['ES'].iloc[-1]
    last_spx = df_zoom['SPX'].iloc[-1]
    last_basis = df_zoom['Basis'].iloc[-1]

    fig.add_annotation(x=0.95, y=last_es, xref="paper", yref="y1", text=f" ES Futures: {last_es:.2f} ", 
                       showarrow=False, bgcolor="#26a69a", font=dict(color="white", size=12), xanchor="right")
    fig.add_annotation(x=0.95, y=last_spx, xref="paper", yref="y1", text=f" SPX Index: {last_spx:.2f} ", 
                       showarrow=False, bgcolor="#ef5350", font=dict(color="white", size=12), xanchor="right", yshift=-25)
    fig.add_annotation(x=0.95, y=last_basis, xref="paper", yref="y2", text=f" Spread: {last_basis:.1f} pts ", 
                       showarrow=False, bgcolor="#7B1FA2", font=dict(color="white", size=12), xanchor="right")

    # --- TITELS & UITLEG ---
    belgian_time = datetime.now(timezone.utc) + timedelta(hours=1)
    timestamp = belgian_time.strftime('%d %b %Y %H:%M') + " CET"

    fig.add_annotation(text=f"<b>CEPHU</b> · ES vs SPX Basis Analysis", 
                       xref="paper", yref="paper", x=0, y=1.12, showarrow=False, font=dict(size=24), xanchor="left")
    
    fig.add_annotation(text=f"Market Pulse Update: {timestamp} | The gap between lines represents the 'Basis'.", 
                       xref="paper", yref="paper", x=0, y=1.06, showarrow=False, xanchor="left", font=dict(size=14, color="grey"))

    # --- EXPORT NAAR HTML ---
    # Gebruik include_plotlyjs='cdn' om het bestand klein te houden
    fig.write_html("index.html", include_plotlyjs='cdn', full_html=False, config={'responsive': True})
    
    # Voeg meta-refresh toe (900 seconden = 15 minuten)
    with open("index.html", "r+") as f:
        content = f.read()
        f.seek(0, 0)
        f.write('<meta http-equiv="refresh" content="900">' + content)
    
    print(f"Success: index.html gegenereerd om {timestamp}.")

if __name__ == "__main__":
    generate_clean_basis_chart_html()
