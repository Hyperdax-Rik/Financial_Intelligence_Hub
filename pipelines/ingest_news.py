import os
import urllib.request
import ssl
import xml.etree.ElementTree as ET
import chromadb
from chromadb.utils import embedding_functions

def fetch_and_store_news(ticker_symbol="AAPL"):
    print(f"Fetching live RSS news feed for {ticker_symbol}...")
    
    rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker_symbol}"
    
    news_items = []
    try:
        req = urllib.request.Request(
            rss_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        
        # Bypass local SSL certificate verification on macOS
        ssl_context = ssl._create_unverified_context()
        
        with urllib.request.urlopen(req, context=ssl_context) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        for item in root.findall('.//item'):
            title = item.find('title').text if item.find('title') is not None else ''
            link = item.find('link').text if item.find('link') is not None else ''
            
            if title:
                news_items.append({
                    'title': title,
                    'publisher': 'Yahoo Finance RSS',
                    'link': link
                })
    except Exception as e:
        print(f"Warning: Could not fetch RSS news for {ticker_symbol}: {e}")

    if not news_items:
        print(f"-> No live RSS news articles retrieved for {ticker_symbol}.")
        return

    # Initialize ChromaDB persistent client
    os.makedirs("data/vector_store", exist_ok=True)
    chroma_client = chromadb.PersistentClient(path="data/vector_store")
    
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    
    collection = chroma_client.get_or_create_collection(
        name="financial_news",
        embedding_function=default_ef
    )

    documents = []
    metadatas = []
    ids = []

    for i, item in enumerate(news_items):
        content = f"{item['title']} - {item['publisher']}"
        uuid = f"{ticker_symbol}_{i}_{hash(item['link']) & 0xffffffff}"
        
        documents.append(content)
        metadatas.append({
            "ticker": ticker_symbol.upper(),
            "publisher": item['publisher'],
            "link": item['link']
        })
        ids.append(uuid)

    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Successfully stored {len(documents)} live RSS news articles for {ticker_symbol} into ChromaDB.")

if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "GOOGL", "TSLA"]
    for t in tickers:
        fetch_and_store_news(t)