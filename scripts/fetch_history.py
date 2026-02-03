import httpx
import os
import json
from dotenv import load_dotenv
load_dotenv()

def fetch_history():
    api_key = os.getenv("GRID_API_KEY")
    url = "https://api-op.grid.gg/live-data-feed/series-state/graphql"
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    
    # Versuche Events zu bekommen
    query = """
    query SeriesEvents {
        seriesEvents(id: "2692648") {
            id
            events {
                type
                occurredAt
                payload
            }
        }
    }
    """
    
    print("--- Versuche Events via GraphQL abzurufen ---")
    with httpx.Client() as client:
        r = client.post(url, headers=headers, json={"query": query})
        if r.status_code == 200:
            data = r.json()
            if "errors" in data:
                print("GraphQL Fehler:", data["errors"][0]["message"])
            else:
                with open("data/raw/events_history.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                print("ERFOLG! Events in data/raw/events_history.json gespeichert.")
        else:
            print(f"Server Fehler: {r.status_code}")

if __name__ == "__main__":
    fetch_history()

