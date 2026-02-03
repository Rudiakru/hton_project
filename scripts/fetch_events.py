import httpx
import os
import json
from dotenv import load_dotenv
load_dotenv()

def fetch_events():
    api_key = os.getenv("GRID_API_KEY")
    # Versuche den REST Events Endpunkt (v1)
    series_id = "2692648"
    url = f"https://api-op.grid.gg/live-data-feed/v1/series/{series_id}/events"
    headers = {"x-api-key": api_key, "Accept": "application/json"}
    
    print(f"--- Rufe Events für ID {series_id} ab ---")
    with httpx.Client() as client:
        try:
            r = client.get(url, headers=headers)
            if r.status_code == 200:
                data = r.json()
                os.makedirs("data/raw", exist_ok=True)
                with open("data/raw/events_data.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("ERFOLG! Events in data/raw/events_data.json gespeichert.")
            else:
                print(f"Server Fehler: {r.status_code}")
                print(r.text)
        except Exception as e:
            print(f"Verbindungsfehler: {e}")

if __name__ == "__main__":
    fetch_events()

