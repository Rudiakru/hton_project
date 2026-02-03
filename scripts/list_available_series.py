import httpx
import os
from dotenv import load_dotenv

def list_series():
    load_dotenv()
    api_key = os.getenv('GRID_API_KEY')
    if not api_key:
        print("Fehler: GRID_API_KEY nicht in .env gefunden.")
        return

    headers = {
        'x-api-key': api_key, 
        'Accept': 'application/json'
    }
    
    # Versuche verschiedene Endpunkte, falls einer nicht geht
    urls = [
        'https://api-op.grid.gg/live-data-feed/v1/series?limit=10',
        'https://api-op.grid.gg/live-data-feed/v1/series'
    ]
    
    for url in urls:
        print(f"Versuche Endpunkt: {url}")
        try:
            with httpx.Client(timeout=10.0) as client:
                r = client.get(url, headers=headers)
                print(f"Status Code: {r.status_code}")
                if r.status_code == 200:
                    data = r.json()
                    # GRID API liefert oft eine Liste direkt oder unter 'results'
                    series_list = data if isinstance(data, list) else data.get('results', [])
                    
                    if not series_list:
                        print("Keine Serien in diesem Endpunkt gefunden.")
                        continue
                        
                    print(f"\nGefundene Serien ({len(series_list)}):")
                    for s in series_list:
                        sid = s.get('id')
                        game = s.get('game', 'N/A')
                        title = s.get('title', 'N/A')
                        print(f"ID: {sid} | Game: {game} | Title: {title}")
                    return # Erfolg
                else:
                    print(f"Fehler-Details: {r.text[:200]}")
        except Exception as e:
            print(f"Verbindungsfehler: {e}")

if __name__ == "__main__":
    list_series()

