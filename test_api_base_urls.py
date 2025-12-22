"""
Test different API base URL patterns to find the actual API endpoint.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("INDIAN_STOCK_API_KEY", "")
TEST_TICKER = "RELIANCE"

# Try different base URL patterns
base_urls = [
    "https://api.indianapi.in",
    "https://indianapi.in/api",
    "https://indianapi.in/api/v1",
    "https://indianapi.in/api/v2",
    "https://indianapi.in/indian-stock-market/api",
    "https://indianapi.in/indian-stock-market",
]

endpoint = "/stock"
headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json"
}
params = {"symbol": TEST_TICKER}

print("Testing different API base URLs...")
print("=" * 60)

for base_url in base_urls:
    full_url = f"{base_url}{endpoint}"
    print(f"\nTesting: {full_url}")
    try:
        response = requests.get(full_url, headers=headers, params=params, timeout=10)
        print(f"  Status: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        # Check if it's JSON
        content_type = response.headers.get('Content-Type', '').lower()
        if 'json' in content_type:
            print(f"  ✓ JSON Response!")
            try:
                data = response.json()
                print(f"  Response keys: {list(data.keys()) if isinstance(data, dict) else 'List/Other'}")
                print(f"  Sample: {str(data)[:200]}...")
            except:
                print(f"  Response: {response.text[:200]}...")
        elif 'html' in content_type:
            print(f"  [X] HTML Response (documentation page)")
        else:
            print(f"  Response preview: {response.text[:200]}...")
    except requests.exceptions.RequestException as e:
        print(f"  Error: {e}")

print("\n" + "=" * 60)
print("Also checking if API key needs to be in different format...")
print("=" * 60)

# Try with the original base URL but check documentation for actual API path
# Maybe the API is at a subdomain or requires a specific path
test_urls = [
    "https://indianapi.in/stock",
    "https://indianapi.in/api/stock",
]

# Try different auth methods
auth_variants = [
    ({"X-API-Key": API_KEY}, "X-API-Key header"),
    ({"Authorization": f"Bearer {API_KEY}"}, "Bearer token"),
    ({"api_key": API_KEY}, "api_key query param"),
]

for url in test_urls:
    for auth_headers, auth_name in auth_variants:
        headers_test = {**auth_headers, "Content-Type": "application/json", "Accept": "application/json"}
        params_test = {"symbol": TEST_TICKER} if "api_key" not in auth_headers else {"symbol": TEST_TICKER, "api_key": API_KEY}
        
        try:
            response = requests.get(url, headers=headers_test, params=params_test, timeout=10)
            content_type = response.headers.get('Content-Type', '').lower()
            if 'json' in content_type and response.status_code == 200:
                print(f"\n✓ FOUND JSON API at: {url}")
                print(f"  Auth method: {auth_name}")
                print(f"  Response: {str(response.json())[:300]}...")
                break
        except:
            pass

