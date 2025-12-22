"""
Test REST-style endpoint patterns for Indian API.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("INDIAN_STOCK_API_KEY", "")
TEST_TICKER = "RELIANCE"

base_urls = [
    "https://indianapi.in",
    "https://api.indianapi.in",
]

# REST-style patterns
patterns = [
    f"/stock/{TEST_TICKER}",
    f"/stock/{TEST_TICKER}/news",
    f"/stock/{TEST_TICKER}/price",
    f"/stock/{TEST_TICKER}/history",
    f"/stocks/{TEST_TICKER}",
]

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

print("Testing REST-style endpoint patterns...")
print("=" * 60)

for base in base_urls:
    print(f"\nBase URL: {base}")
    for pattern in patterns:
        url = f"{base}{pattern}"
        print(f"\n  Testing: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            content_type = response.headers.get('Content-Type', '').lower()
            
            if 'json' in content_type and response.status_code == 200:
                print(f"    [SUCCESS] JSON Response!")
                data = response.json()
                print(f"    Keys: {list(data.keys()) if isinstance(data, dict) else 'List'}")
                print(f"    Sample: {str(data)[:200]}...")
            elif response.status_code == 401:
                print(f"    [AUTH ERROR] 401 - Check API key")
            elif response.status_code == 404:
                print(f"    [NOT FOUND] 404")
            else:
                print(f"    Status: {response.status_code}, Type: {content_type}")
        except Exception as e:
            print(f"    Error: {e}")

# Also try with query params on REST endpoints
print("\n" + "=" * 60)
print("Testing REST endpoints with query params...")
print("=" * 60)

for base in base_urls:
    url = f"{base}/stock/{TEST_TICKER}"
    params_variants = [
        {"news": "true"},
        {"price": "true"},
        {"history": "true"},
        {"data": "all"},
    ]
    
    for params in params_variants:
        print(f"\n  Testing: {url} with {params}")
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            content_type = response.headers.get('Content-Type', '').lower()
            
            if 'json' in content_type and response.status_code == 200:
                print(f"    [SUCCESS] JSON Response!")
                try:
                    data = response.json()
                    print(f"    Sample: {str(data)[:200]}...")
                except:
                    print(f"    Response: {response.text[:200]}...")
            else:
                print(f"    Status: {response.status_code}")
        except Exception as e:
            print(f"    Error: {e}")

