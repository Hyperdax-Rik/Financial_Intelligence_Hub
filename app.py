import streamlit as st
import os
import glob
import yfinance as yf
import plotly.graph_objects as go
from agents.pure_pipeline import FinancialIntelligenceHub

# --- Page Configuration ---
st.set_page_config(
    page_title="Financial Intelligence Hub | Enterprise",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Premium Midnight & Frosted Glass CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    .stApp {
        background: linear-gradient(160deg, #0f172a 0%, #090d16 50%, #05070a 100%);
        color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-attachment: fixed;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0e1526;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
    [data-testid="stSidebar"] * {
        color: #cbd5e1 !important;
    }

    .hero-container {
        padding: 1.5rem 0rem 1rem 0rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 2rem;
    }
    .main-title {
        font-size: 2.25rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        color: #ffffff;
        margin-bottom: 0.25rem;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #94a3b8;
        font-weight: 400;
    }

    div.stMetric {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 1rem;
        border-radius: 12px;
        backdrop-filter: blur(12px);
    }

    .stButton > button {
        background: #10b981;
        color: #ffffff;
        font-weight: 600;
        font-size: 0.9rem;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.25);
    }
    .stButton > button:hover {
        background: #059669;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
    }

    .stDownloadButton > button {
        background-color: rgba(30, 41, 59, 0.7);
        color: #f1f5f9;
        font-weight: 500;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 0.5rem 1rem;
        width: 100%;
        transition: all 0.2s ease;
    }
    .stDownloadButton > button:hover {
        background-color: rgba(51, 65, 85, 0.8);
        border-color: #10b981;
        color: #34d399;
    }
</style>
""", unsafe_allow_html=True)

# --- Header Section ---
st.markdown("""
<div class="hero-container">
    <div class="main-title">Financial Intelligence Hub</div>
    <div class="sub-title">Autonomous Multi-Agent Market Memos, Real-Time Volatility Analysis & Institutional Sentiment Engine</div>
</div>
""", unsafe_allow_html=True)

os.makedirs("reports", exist_ok=True)

# --- Sidebar Controls ---
st.sidebar.markdown("### ⚙️ Command Center")
ticker_input = st.sidebar.text_input("Watchlist Tickers (comma-separated)", value="AAPL, MSFT, NVDA")
run_button = st.sidebar.button("Run Intelligence Pipeline", use_container_width=True)

# --- Pipeline Execution Handler ---
if run_button:
    tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]
    if not tickers:
        st.sidebar.error("Please enter at least one valid ticker.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, ticker in enumerate(tickers):
            status_text.markdown(f"⏳ **Analyzing {ticker}** via agent pipeline...")
            try:
                hub = FinancialIntelligenceHub(ticker)
                memo = hub.run_pipeline()
                filename = f"reports/{ticker}_investment_memo.md"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(memo)
            except Exception as e:
                st.error(f"Error processing {ticker}: {e}")
            
            progress_bar.progress((idx + 1) / len(tickers))
        
        # Cleanup progress UI
        progress_bar.empty()
        status_text.empty()
        st.sidebar.success("🎉 Intelligence Pipeline Completed Successfully!")
        
        # Save the primary processed ticker to session state so it auto-selects
        st.session_state["selected_target_ticker"] = tickers[0]
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 Dossier Library")

# Scan available report files from disk
report_files = glob.glob("reports/*_investment_memo.md")
report_tickers = sorted([os.path.basename(f).replace("_investment_memo.md", "") for f in report_files])

if report_tickers:
    # Ensure session state has a valid default
    if "selected_target_ticker" not in st.session_state or st.session_state["selected_target_ticker"] not in report_tickers:
        st.session_state["selected_target_ticker"] = report_tickers[0]
    
    # Render selectbox bound to session state
    selected_ticker = st.sidebar.selectbox(
        "Select Target Asset", 
        report_tickers,
        key="selected_target_ticker"
    )
else:
    selected_ticker = "None"
    st.sidebar.info("No reports generated yet. Run the pipeline above.")

# --- Chart & Analytics Engine ---
def render_live_chart(ticker_symbol):
    try:
        stock = yf.Ticker(ticker_symbol)
        df = stock.history(period="3mo")
        
        if df.empty:
            return None, None
            
        latest_close = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        change = latest_close - prev_close
        pct_change = (change / prev_close) * 100
        
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            increasing_line_color='#10b981', 
            decreasing_line_color='#f43f5e',
            name="Price"
        )])
        
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(
            x=df.index, 
            y=df['SMA20'], 
            mode='lines', 
            name='20-Day SMA',
            line=dict(color='#38bdf8', width=1.5)
        ))
        
        fig.update_layout(
            title=dict(text=f"{ticker_symbol} Price Structure & Trend", font=dict(color="#f1f5f9", size=14, family="Inter")),
            yaxis_title=dict(text="USD ($)", font=dict(color="#94a3b8", size=12)),
            xaxis_rangeslider_visible=False,
            template="plotly_dark",
            height=370,
            margin=dict(l=10, r=10, t=35, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Inter, sans-serif", color="#94a3b8"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        metrics = {
            "price": f"${latest_close:.2f}",
            "change": f"{change:+.2f} ({pct_change:+.2f}%)",
            "volume": f"{df['Volume'].iloc[-1]:,}",
            "high": f"${df['High'].iloc[-1]:.2f}",
            "low": f"${df['Low'].iloc[-1]:.2f}"
        }
        
        return fig, metrics
    except Exception as e:
        return None, None

# --- Main Dashboard Viewport ---
if selected_ticker and selected_ticker != "None":
    st.markdown(f"### Executive Intelligence Dossier: <span style='color:#34d399;'>{selected_ticker}</span>", unsafe_allow_html=True)
    
    fig, metrics = render_live_chart(selected_ticker)
    
    if metrics:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Latest Close", metrics["price"], metrics["change"])
        col2.metric("24h Volume", metrics["volume"])
        col3.metric("Session High", metrics["high"])
        col4.metric("Session Low", metrics["low"])
        st.markdown("<br>", unsafe_allow_html=True)

    chart_col, memo_col = st.columns([1.1, 1], gap="large")
    
    with chart_col:
        st.markdown("#### Technical Market Structure")
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"Could not load live chart data for {selected_ticker}.")
            
    with memo_col:
        st.markdown("#### Dossier Export & Controls")
        report_path = f"reports/{selected_ticker}_investment_memo.md"
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                memo_content = f.read()
            
            st.success(f"Dossier compiled successfully. Word count: {len(memo_content.split())} words.")
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label=f"Export {selected_ticker} Dossier (.md)",
                data=memo_content,
                file_name=f"{selected_ticker}_investment_memo.md",
                mime="text/markdown",
                use_container_width=True
            )
    
    st.markdown("<hr style='border: 1px solid rgba(255, 255, 255, 0.08); margin: 2rem 0;'>", unsafe_allow_html=True)
    st.markdown("#### Comprehensive Investment Memo")
    st.markdown(memo_content, unsafe_allow_html=True)

else:
    st.info("Select a dossier from the sidebar library or run the intelligence pipeline to generate a new report.")