import duckdb
import pandas as pd

def run_analytical_queries(db_path="data/finance_hub.db"):
    print("Connecting to DuckDB for analytics modeling...")
    conn = duckdb.connect(db_path)
    
    # 1. Check available tables
    tables = conn.execute("SHOW TABLES;").fetchdf()
    print("Tables in database:\n", tables)
    
    # 2. Compute key technical and risk metrics using a CTE to prevent nested window function errors
    query = """
    CREATE OR REPLACE TABLE stock_analytics AS 
    WITH base_returns AS (
        SELECT 
            ticker,
            date,
            close,
            volume,
            -- Calculate Daily Returns in step 1
            (close - LAG(close, 1) OVER (PARTITION BY ticker ORDER BY date)) / 
            NULLIF(LAG(close, 1) OVER (PARTITION BY ticker ORDER BY date), 0) AS daily_return
        FROM stock_prices
    )
    SELECT 
        ticker,
        date,
        close,
        volume,
        daily_return,
        -- Calculate 7-day and 30-day Moving Averages on closing price
        AVG(close) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as ma_7d,
        AVG(close) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) as ma_30d,
        -- Rolling 30-day Volatility (Standard Deviation of daily returns)
        STDDEV(daily_return) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) as volatility_30d
    FROM base_returns;
    """
    
    conn.execute(query)
    print("Successfully created 'stock_analytics' table with computed financial KPIs!")
    
    # Preview sample computed analytics for AAPL
    sample_df = conn.execute("SELECT ticker, date, close, daily_return, ma_7d, volatility_30d FROM stock_analytics WHERE ticker = 'AAPL' ORDER BY date DESC LIMIT 5;").fetchdf()
    print("\nSample Analytics Output (AAPL):")
    print(sample_df)
    
    conn.close()

if __name__ == "__main__":
    run_analytical_queries()