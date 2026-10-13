import os
import duckdb
import yfinance as yf
import pandas as pd

def fetch_market_data(ticker_symbol="AAPL", period="6mo"):
    print(f"Fetching market data for {ticker_symbol}...")
    stock = yf.Ticker(ticker_symbol)
    df = stock.history(period=period)
    
    if df.empty:
        print(f"No data found for {ticker_symbol}")
        return None
        
    df.reset_index(inplace=True)
    # Clean column names for SQL compatibility (e.g., 'Stock Splits' -> 'stock_splits')
    df.columns = [col.lower().replace(" ", "_").replace(".", "") for col in df.columns]
    df['ticker'] = ticker_symbol.upper()
    
    # Ensure date column is standard string/date format
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date']).dt.date

    return df

def save_to_duckdb(df, table_name="stock_prices"):
    os.makedirs("data", exist_ok=True)
    conn = duckdb.connect("data/finance_hub.db")
    
    # Create table if it doesn't exist
    conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM df WHERE 1=0")
    
    # Upsert or append logic: delete existing rows for this ticker to avoid duplicates, then insert
    ticker = df['ticker'].iloc[0]
    conn.execute(f"DELETE FROM {table_name} WHERE ticker = ?", [ticker])
    
    conn.execute(f"INSERT INTO {table_name} SELECT * FROM df")
    print(f"Successfully stored {len(df)} rows for {ticker} into DuckDB table: {table_name}")
    conn.close()

if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "GOOGL", "TSLA"]
    for t in tickers:
        data = fetch_market_data(t)
        if data is not None:
            save_to_duckdb(data)