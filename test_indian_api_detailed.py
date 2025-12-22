"""
Detailed diagnostic script to test Indian API endpoints and discover correct format.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("INDIAN_STOCK_API_KEY", "")
BASE_URL = "https://indianapi.in"
TEST_TICKER = "RELIANCE"

print(f"Testing Indian API with ticker: {TEST_TICKER}")
print(f"API Key: {API_KEY[:10]}...{API_KEY[-5:] if len(API_KEY) > 15 else 'N/A'}")
print(f"Base URL: {BASE_URL}")
print()

# Test different authentication methods
auth_methods = [
    ("X-API-Key header", {"X-API-Key": API_KEY}),
    ("Authorization Bearer", {"Authorization": f"Bearer {API_KEY}"}),
    ("Authorization Token", {"Authorization": f"Token {API_KEY}"}),
    ("api_key query param", None),  # Will add to params
]

# Test /stock endpoint with different parameter formats
endpoint = f"{BASE_URL}/stock"
param_variants = [
    {"symbol": TEST_TICKER},
    {"ticker": TEST_TICKER},
    {"stock": TEST_TICKER},
    {"symbol": TEST_TICKER, "data": "all"},
    {"symbol": TEST_TICKER, "include": "news,price"},
]

print("=" * 60)
print("Testing /stock endpoint")
print("=" * 60)

for auth_name, auth_headers in auth_methods:
    print(f"\n--- Testing with {auth_name} ---")
    
    for params in param_variants:
        # Add API key to params if using query param auth
        if auth_headers is None:
            test_params = {**params, "api_key": API_KEY}
            test_headers = {"Content-Type": "application/json", "Accept": "application/json"}
        else:
            test_params = params
            test_headers = {**auth_headers, "Content-Type": "application/json", "Accept": "application/json"}
        
        try:
            print(f"  Trying: {endpoint} with params={test_params}")
            response = requests.get(endpoint, headers=test_headers, params=test_params, timeout=10)
            print(f"    Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"    SUCCESS! Response preview:")
                try:
                    data = response.json()
                    print(f"    Response keys: {list(data.keys()) if isinstance(data, dict) else 'List/Other'}")
                    print(f"    Response sample: {str(data)[:200]}...")
                except:
                    print(f"    Response text: {response.text[:200]}...")
                break
            elif response.status_code == 401:
                print(f"    Authentication failed (401)")
            elif response.status_code == 404:
                print(f"    Endpoint not found (404)")
            else:
                print(f"    Error response: {response.text[:200]}")
        except requests.exceptions.RequestException as e:
            print(f"    Request failed: {e}")

print("\n" + "=" * 60)
print("Testing /search endpoint")
print("=" * 60)

# Test /search endpoint
search_endpoint = f"{BASE_URL}/search"
search_params_variants = [
    {"q": TEST_TICKER},
    {"query": TEST_TICKER},
    {"symbol": TEST_TICKER},
    {"stock": TEST_TICKER},
]

for auth_name, auth_headers in auth_methods[:1]:  # Just test first auth method for search
    print(f"\n--- Testing /search with {auth_name} ---")
    
    for params in search_params_variants:
        if auth_headers is None:
            test_params = {**params, "api_key": API_KEY}
            test_headers = {"Content-Type": "application/json", "Accept": "application/json"}
        else:
            test_params = params
            test_headers = {**auth_headers, "Content-Type": "application/json", "Accept": "application/json"}
        
        try:
            print(f"  Trying: {search_endpoint} with params={test_params}")
            response = requests.get(search_endpoint, headers=test_headers, params=test_params, timeout=10)
            print(f"    Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"    SUCCESS! Response preview:")
                try:
                    data = response.json()
                    print(f"    Response: {str(data)[:300]}...")
                except:
                    print(f"    Response text: {response.text[:300]}...")
        except requests.exceptions.RequestException as e:
            print(f"    Request failed: {e}")

print("\n" + "=" * 60)
print("Testing /trending endpoint")
print("=" * 60)

# Test /trending endpoint (might not need params)
trending_endpoint = f"{BASE_URL}/trending"
auth_headers = {"X-API-Key": API_KEY, "Content-Type": "application/json", "Accept": "application/json"}

try:
    print(f"Trying: {trending_endpoint}")
    response = requests.get(trending_endpoint, headers=auth_headers, timeout=10)
    print(f"  Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"  SUCCESS! Response preview:")
        try:
            data = response.json()
            print(f"  Response: {str(data)[:300]}...")
        except:
            print(f"  Response text: {response.text[:300]}...")
    else:
        print(f"  Error: {response.text[:200]}")
except requests.exceptions.RequestException as e:
    print(f"  Request failed: {e}")

