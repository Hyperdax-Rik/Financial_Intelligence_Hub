Markdown
# ⚡ Financial Market & Sentiment Intelligence Hub

An autonomous, production-grade multi-agent financial analytics platform featuring a sleek Midnight-Slate Streamlit dashboard, real-time market charting, and institutional-grade investment memo generation.

---

## 🚀 Key Features

* **🤖 Autonomous Multi-Agent Pipeline:** Coordinates specialized agents (Data Scout, Quant Analyst, Risk Assessor, and Writer) to process tickers and build comprehensive markdown dossiers.
* **📈 Real-Time & Fallback Analytics:** Powered by `yfinance` for live pricing, volume tracking, and technical indicators (20-day SMA), paired with local database storage.
* **📊 Interactive Visualizations:** Dynamic Plotly candlestick charts with responsive zoom, custom tooltips, and session performance metrics.
* **🎨 Enterprise Midnight-Slate UI:** Designed with a refined dark-mode aesthetic, frosted-glass panels, and auto-focus report rendering upon pipeline completion.

---

## 🛠️ Tech Stack

* **Frontend/UI:** Streamlit, Plotly, Custom CSS (Midnight-Slate Theme)
* **Backend Intelligence:** Groq API (`llama-3.3`), Multi-agent orchestration
* **Data Layer:** DuckDB, ChromaDB, `yfinance`

---

## ⚙️ Quick Start

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/financial_intelligence_hub.git](https://github.com/YOUR_USERNAME/financial_intelligence_hub.git)
   cd financial_intelligence_hub
**Install dependencies:**
```bash
pip install -r requirements.txt
```
**Set your Groq API key:**
Linux/macOS: export GROQ_API_KEY="your_api_key_here"
Windows (PowerShell): $env:GROQ_API_KEY="your_api_key_here"

**Launch the application:**
```bash
streamlit run app.py
