import httpx
import os
import json
from dotenv import load_dotenv
load_dotenv()

def fetch():
    api_key = os.getenv("GRID_API_KEY")
    url = "https://api-op.grid.gg/live-data-feed/series-state/graphql"
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    
    query = """
    query SeriesState {
        seriesState(id: "2692648") {
            id
            games {
                teams {
                    players {
                        id
                        name
                        position { x y }
                    }
                }
            }
        }
    }
    """
    
    print("--- Starte Abruf für ID 2692648 ---")
    with httpx.Client() as client:
        try:
            r = client.post(url, headers=headers, json={"query": query})
            if r.status_code == 200:
                data = r.json()
                if "errors" in data:
                    print("GraphQL Fehler:", data["errors"][0]["message"])
                else:
                    os.makedirs("data/raw", exist_ok=True)
                    with open("data/raw/real_data.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                    print("ERFOLG! Daten in data/raw/real_data.json gespeichert.")
            else:
                print(f"Server Fehler: {r.status_code}")
                print(r.text)
        except Exception as e:
            print(f"Verbindungsfehler: {e}")

if __name__ == "__main__":
    fetch()

