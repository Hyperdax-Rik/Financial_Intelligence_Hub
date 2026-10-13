import duckdb
import chromadb
from crewai.tools import tool

class FinancialDataTools:
    
    @tool("Query Stock Analytics Database")
    def query_stock_analytics(sql_query: str) -> str:
        """
        Executes a SQL query on the DuckDB 'stock_analytics' or 'stock_prices' table.
        Use this tool to fetch closing prices, daily returns, moving averages, or volatility metrics.
        Example query: SELECT * FROM stock_analytics WHERE ticker = 'AAPL' ORDER BY date DESC LIMIT 5;
        """
        try:
            conn = duckdb.connect("data/finance_hub.db", read_only=True)
            df = conn.execute(sql_query.strip()).fetchdf()
            conn.close()
            if df.empty:
                return "Query returned no results."
            return df.to_markdown(index=False)
        except Exception as e:
            return f"Error executing SQL query: {e}"

    @tool("Search Financial News and Sentiment Vector Store")
    def search_news_sentiment(query_text: str) -> str:
        """
        Searches the ChromaDB vector store for recent news headlines, press releases, 
        and market sentiment related to a ticker or market trend.
        """
        try:
            chroma_client = chromadb.PersistentClient(path="data/vector_store")
            collection = chroma_client.get_collection("financial_news")
            
            results = collection.query(
                query_texts=[query_text],
                n_results=3
            )
            
            documents = results.get('documents', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]
            
            if not documents:
                return "No relevant news articles found."
                
            formatted_output = ""
            for doc, meta in zip(documents, metadatas):
                formatted_output += f"- {doc} (Publisher: {meta.get('publisher')})\n"
                
            return formatted_output
        except Exception as e:
            return f"Error searching vector store: {e}"