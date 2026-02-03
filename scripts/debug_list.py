import httpx
import os
from dotenv import load_dotenv

def debug_list_series():
    load_dotenv()
    api_key = os.getenv('GRID_API_KEY')
    headers = {'x-api-key': api_key, 'Accept': 'application/json'}
    url = 'https://api.grid.gg/live-data-feed/v1/series'
    
    print(f"Debug Abfrage: {url}")
    try:
        with httpx.Client() as client:
            r = client.get(url, headers=headers)
            print(f"Status: {r.status_code}")
            print(f"Response: {r.text[:500]}")
    except Exception as e:
        print(f"Fehler: {e}")

if __name__ == "__main__":
    debug_list_series()

