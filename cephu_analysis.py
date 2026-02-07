import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

def generate_cephu_chart():
    # 1. Data ophalen (ES=F is de E-mini S&P 500 Future, ^GSPC is de SPX Index)
    # We halen 5 dagen aan 1-minuut data op
    future = yf.download("ES=F", period="5d", interval="1m", progress=False)
    index = yf.download("^GSPC", period="5d", interval="1m", progress=False)

    if future.empty or index.empty:
        print("Geen data van yfinance. GitHub Action stopt hier.")
        exit(0)

    # Data samenvoegen op tijdstip
    df = pd.DataFrame()
    df['MES'] = future['Close']
    df['SPX'] = index['Close']
    df = df.dropna()

    # 2. Berekeningen
    df['Basis'] = df['MES'] - df['SPX']
    df['Basis_MA'] = df['Basis'].rolling(window=20).mean()
    
    last_basis = df['Basis'].iloc[-1]
    avg_basis = df['Basis_MA'].iloc[-1]
    diff = last_basis - avg_basis
    belgian_time = datetime.utcnow() + timedelta(hours=1)
    timestamp = belgian_time.strftime("%B %d, %Y | %H:%M") + " CET"

    # Takeaway logica
    if last_basis > avg_basis:
        tk_title, tk_text, tk_color = "BULLISH MOMENTUM", f"The future is trading {diff:.2f} points above average.", "green"
    else:
        tk_title, tk_text, tk_color = "BEARISH BIAS", f"The future is trading {abs(diff):.2f} points below average.", "red"

    # 3. Grafiek Setup
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.12, 
        row_heights=[0.65, 0.35]
    )

    # Kleuren uit Cephu palet
    ACCENT_RED = "hsl(2, 39, 47)"
    BG_COLOR = "hsl(0, 0, 96)"
    GREY_GREEN = "hsl(106, 5, 52)"

    # Traces
    fig.add_trace(go.Scatter(x=df.index, y=df['MES'], name="MES Future", line=dict(color=ACCENT_RED, width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SPX'], name="SPX Index", line=dict(color=GREY_GREEN, width=1, dash='dot')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Basis'], fill='tozeroy', line=dict(color="orange", width=0.5), fillcolor='rgba(255, 165, 0, 0.2)'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Basis_MA'], line=dict(color="black", width=1.5)), row=2, col=1)

    # 4. Annotaties & Labels
    # Subplot titels linksonder
    fig.add_annotation(text="PRICE COMPARISON: FUTURE VS INDEX", xref="paper", yref="paper", x=0, y=1, showarrow=False, font=dict(size=11, color="grey"), xanchor="left", yanchor="bottom")
    fig.add_annotation(text="BASIS ANALYSIS: POINTS DEVIATION", xref="paper", yref="paper", x=0, y=0.35, showarrow=False, font=dict(size=11, color="orange"), xanchor="left", yanchor="bottom")
    
    # Update tijd rechtsboven
    fig.add_annotation(text=f"Last updated: {timestamp}", xref="paper", yref="paper", x=1, y=1.08, showarrow=False, font=dict(size=10, color="grey"), xanchor="right")

    # Key Takeaway onderaan
    fig.add_annotation(
        text=f"<b>Key Takeaway:</b> <span style='color:{tk_color}'>{tk_title}</span> — {tk_text}",
        xref="paper", yref="paper", x=0, y=-0.3, showarrow=False, font=dict(size=15, family="Helvetica Neue"), xanchor="left", align="left"
    )

    # 5. Layout & As-instellingen (Geen ticks/streepjes)
    fig.update_layout(
        template="simple_white",
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        margin=dict(l=50, r=20, t=100, b=150),
        showlegend=False,
        hovermode="x unified",
        font=dict(family="Helvetica Neue", size=16)
    )

    fig.update_xaxes(showline=False, showgrid=False, zeroline=False, ticks="")
    fig.update_yaxes(showline=False, showgrid=True, gridcolor="rgba(0,0,0,0.05)", zeroline=False, ticks="")

    # 6. Exporteren met Auto-Refresh Meta Tag
    fig.write_html("index.html", include_plotlyjs='cdn', full_html=True)
    
    # Voeg meta tag toe voor browser refresh (elke 5 min)
    with open("index.html", "r+") as f:
        content = f.read()
        f.seek(0, 0)
        f.write('<meta http-equiv="refresh" content="300">' + content)

if __name__ == "__main__":
    generate_cephu_chart()
