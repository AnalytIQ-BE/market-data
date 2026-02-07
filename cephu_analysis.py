import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

def generate_cephu_chart():
    # 1. Data ophalen (2 dagen om ook in het weekend de laatste actieve data te tonen)
    future = yf.download("ES=F", period="2d", interval="1m", progress=False)
    index = yf.download("^GSPC", period="2d", interval="1m", progress=False)

    if future.empty or index.empty:
        print("Geen data gevonden.")
        return

    # Data samenvoegen en opschonen
    df = pd.merge(future['Close'], index['Close'], left_index=True, right_index=True, how='inner')
    df.columns = ['MES', 'SPX']
    df = df.dropna()

    # 2. Berekeningen
    df['Basis'] = df['MES'] - df['SPX']
    df['Basis_MA'] = df['Basis'].rolling(window=20).mean()
    
    last_basis = df['Basis'].iloc[-1]
    avg_basis = df['Basis_MA'].iloc[-1]
    diff = last_basis - avg_basis

    # TIJDZONE FIX: Forceer Belgische tijd (UTC + 1)
    belgian_time = datetime.utcnow() + timedelta(hours=1)
    timestamp = belgian_time.strftime("%B %d, %Y | %H:%M") + " CET"

    # Takeaway logica
    if last_basis > avg_basis:
        tk_title, tk_text, tk_color = "BULLISH MOMENTUM", f"The future is trading {diff:.2f} points above average.", "green"
    else:
        tk_title, tk_text, tk_color = "BEARISH BIAS", f"The future is trading {abs(diff):.2f} points below average.", "red"

    # 3. Grafiek Setup
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12, row_heights=[0.65, 0.35])

    # Traces
    fig.add_trace(go.Scatter(x=df.index, y=df['MES'], name="MES", line=dict(color="hsl(2, 39, 47)", width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['SPX'], name="SPX", line=dict(color="hsl(106, 5, 52)", width=1, dash='dot')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Basis'], fill='tozeroy', line=dict(color="orange", width=0.5), fillcolor='rgba(255, 165, 0, 0.2)'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Basis_MA'], line=dict(color="black", width=1.5)), row=2, col=1)

    # 4. Annotaties (Titels onderaan de subplots)
    fig.add_annotation(text="PRICE COMPARISON: FUTURE VS INDEX", xref="paper", yref="paper", x=0, y=1, showarrow=False, font=dict(size=11, color="grey"), xanchor="left", yanchor="bottom")
    fig.add_annotation(text="BASIS ANALYSIS: POINTS DEVIATION", xref="paper", yref="paper", x=0, y=0.35, showarrow=False, font=dict(size=11, color="orange"), xanchor="left", yanchor="bottom")
    fig.add_annotation(text=f"Last updated: {timestamp}", xref="paper", yref="paper", x=1, y=1.08, showarrow=False, font=dict(size=10, color="grey"), xanchor="right")
    
    # Key Takeaway
    fig.add_annotation(text=f"<b>Key Takeaway:</b> <span style='color:{tk_color}'>{tk_title}</span> — {tk_text}", xref="paper", yref="paper", x=0, y=-0.12, showarrow=False, font=dict(size=16), xanchor="left")

    # 5. Layout & As-instellingen (GEEN TICKS)
    fig.update_layout(
        template="simple_white",
        paper_bgcolor="hsl(0, 0, 96)",
        plot_bgcolor="hsl(0, 0, 96)",
        margin=dict(l=50, r=20, t=80, b=80),
        showlegend=False,
        font=dict(family="Helvetica Neue", size=16)
    )

    # Verwijder streepjes (ticks) op beide assen
    fig.update_xaxes(showline=False, showgrid=False, zeroline=False, ticks="")
    fig.update_yaxes(showline=False, showgrid=True, gridcolor="rgba(0,0,0,0.05)", zeroline=False, ticks="")

    # 6. Export met Meta-Refresh (voor Squarespace caching)
    fig.write_html("index.html", include_plotlyjs='cdn', full_html=True)
    with open("index.html", "r+") as f:
        content = f.read()
        f.seek(0, 0)
        f.write('<meta http-equiv="refresh" content="300">' + content)

if __name__ == "__main__":
    generate_cephu_chart()
