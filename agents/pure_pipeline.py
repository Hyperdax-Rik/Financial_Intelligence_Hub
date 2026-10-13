import os
import sys
import time
import argparse
from groq import Groq
import duckdb
import chromadb
import yfinance as yf
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class FinancialIntelligenceHub:
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "openai/gpt-oss-120b"

    def _call_llm(self, system_prompt: str, user_prompt: str, max_retries=3) -> str:
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1
                )
                return response.choices[0].message.content
            except Exception as e:
                if "413" in str(e) or "rate_limit" in str(e):
                    wait_time = (attempt + 1) * 20
                    print(f"⚠️ Rate limit hit for {self.ticker}. Backing off for {wait_time}s (Attempt {attempt+1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    raise e
        raise Exception(f"Max retries reached for {self.ticker} due to rate limits.")

    def query_stock_analytics(self) -> str:
        """Tries local DuckDB first. If empty or missing, fetches live data via yfinance."""
        try:
            conn = duckdb.connect("data/finance_hub.db", read_only=True)
            # Check if table exists and has rows for this ticker
            tables = conn.execute("SHOW TABLES;").fetchall()
            table_names = [t[0] for t in tables]
            
            if "stock_analytics" in table_names:
                df = conn.execute(f"SELECT * FROM stock_analytics WHERE ticker = '{self.ticker}' ORDER BY date DESC LIMIT 3;").fetchdf()
                conn.close()
                if not df.empty:
                    print(f"📂 Loaded historical data for {self.ticker} from local DuckDB.")
                    try:
                        return df.to_markdown(index=False)
                    except ImportError:
                        return df.to_string(index=False)
            else:
                conn.close()
        except Exception as e:
            pass  # Fallback to live fetch if local DB fails

        # Live Fallback via yfinance
        print(f"🌐 Fetching live real-time market data for {self.ticker} via Yahoo Finance...")
        try:
            stock = yf.Ticker(self.ticker)
            df = stock.history(period="5d")  # Get last 5 days
            if df.empty:
                return f"No live or local market data found for {self.ticker}."
            
            # Format dataframe to match expected structure
            df.reset_index(inplace=True)
            df['ticker'] = self.ticker
            # Keep core columns
            cols_to_show = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            df = df[[c for c in cols_to_show if c in df.columns]]
            df = df.tail(3) # Limit to 3 recent rows
            
            try:
                return df.to_markdown(index=False)
            except ImportError:
                return df.to_string(index=False)
        except Exception as e:
            return f"Error fetching live data via yfinance: {e}"

    def search_news_sentiment(self, query_text: str) -> str:
        try:
            chroma_client = chromadb.PersistentClient(path="data/vector_store")
            collection = chroma_client.get_collection("financial_news")
            results = collection.query(query_texts=[query_text], n_results=2)
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            
            if not documents:
                return f"No specific vector news found for {query_text}. Relying on model market awareness."
                
            formatted_output = ""
            for doc, meta in zip(documents, metadatas):
                publisher = meta.get('publisher', 'Unknown') if meta else 'Unknown'
                formatted_output += f"- {doc} (Publisher: {publisher})\n"
            return formatted_output
        except Exception as e:
            return f"Error searching vector store: {e}"

    def run_pipeline(self):
        print(f"\n🚀 Running Intelligence Pipeline for {self.ticker}...")

        sql_data = self.query_stock_analytics()
        news_data = self.search_news_sentiment(self.ticker)
        
        scout_summary = f"### Recent Price Action ({self.ticker}):\n{sql_data}\n\n### Recent News:\n{news_data}"

        quant_prompt = f"You are an expert financial analyst. Provide a concise bulleted analysis of technical indicators, volatility trends, and momentum for {self.ticker} based on the data."
        quant_output = self._call_llm(quant_prompt, scout_summary)

        risk_prompt = f"You are a risk manager. Identify short-term market risks or catalysts for {self.ticker} based on the news and current market conditions."
        risk_output = self._call_llm(risk_prompt, scout_summary)

        writer_system = "You are a senior financial writer who crafts rigorous, concise executive investment memos in Markdown format."
        writer_user = f"""
        Synthesize the following analysis into a concise professional investment memo for {self.ticker}.
        
        ### Quantitative Findings:
        {quant_output}

        ### Risk & Sentiment Assessment:
        {risk_output}
        """
        final_memo = self._call_llm(writer_system, writer_user)
        return final_memo

def run_batch_pipeline(tickers: list[str]):
    os.makedirs("reports", exist_ok=True)
    
    for i, ticker in enumerate(tickers):
        ticker = ticker.strip().upper()
        if not ticker:
            continue
        try:
            hub = FinancialIntelligenceHub(ticker)
            memo = hub.run_pipeline()
            
            filename = f"reports/{ticker}_investment_memo.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(memo)
                
            print(f"✅ Successfully generated and saved report for {ticker} -> {filename}")
            
            if i < len(tickers) - 1:
                print("⏳ Pausing 20 seconds to reset Groq token bucket...")
                time.sleep(20)
                
        except Exception as e:
            print(f"❌ Error processing {ticker}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Financial Market & Sentiment Intelligence Hub")
    parser.add_argument("--tickers", type=str, help="Comma-separated list of tickers (e.g., AAPL,MSFT,NVDA)")
    parser.add_argument("--file", type=str, help="Path to a text file containing tickers (one per line)")
    
    args = parser.parse_args()
    watchlist = []
    
    if args.tickers:
        watchlist = args.tickers.split(",")
    elif args.file and os.path.exists(args.file):
        with open(args.file, "r") as f:
            watchlist = [line.strip() for line in f if line.strip()]
    else:
        user_input = input("📊 Enter tickers separated by commas (default: AAPL, MSFT, GOOGL, TSLA): ").strip()
        if user_input:
            watchlist = user_input.split(",")
        else:
            watchlist = ["AAPL", "MSFT", "GOOGL", "TSLA"]
            
    print(f"\n📊 Starting Batch Processing for Watchlist: {[t.strip().upper() for t in watchlist]}")
    run_batch_pipeline(watchlist)
    print("\n🎉 Batch Processing Complete! All reports saved in the 'reports/' directory.")