
import os
import requests
from dotenv import load_dotenv
from textblob import TextBlob

load_dotenv()

api_key = os.environ.get("BRAVE_API_KEY")
print(f"API Key found: {api_key is not None}")
if api_key:
    print(f"Key preview: {api_key[:4]}...")

def test_fetch_news(symbol):
    print(f"Testing fetch news for {symbol}...")
    query = f"{symbol} forex news analysis outlook"
    url = "https://api.search.brave.com/res/v1/news/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }
    params = {"q": query, "count": 1}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            print(f"Found {len(results)} results.")
            if results:
                title = results[0].get('title', '')
                desc = results[0].get('description', '')
                print("First result title:", title)
                
                # Test TextBlob
                print("Testing TextBlob analysis...")
                text = f"{title} {desc}"
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity
                print(f"Polarity: {polarity}")
                
        else:
            print("Response:", response.text)
    except Exception as e:
        print(f"Exception details: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_fetch_news("EURUSD")
