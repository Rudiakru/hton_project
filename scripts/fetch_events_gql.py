import httpx
import os
import json
from dotenv import load_dotenv
load_dotenv()

def fetch_events_gql():
    api_key = os.getenv("GRID_API_KEY")
    # Wir nutzen den gleichen Basis-URL wie beim erfolgreichen State-Abruf
    url = "https://api-op.grid.gg/live-data-feed/series-state/graphql"
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    
    # GraphQL Query für Events innerhalb von seriesState
    query = """
    query SeriesStateWithEvents {
        seriesState(id: "2692648") {
            id
            events {
                type
                occurredAt
                payload
            }
        }
    }
    """
    
    print("--- Starte GraphQL Event-Abruf für ID 2692648 ---")
    with httpx.Client() as client:
        try:
            r = client.post(url, headers=headers, json={"query": query})
            if r.status_code == 200:
                data = r.json()
                if "errors" in data:
                    print("GraphQL Fehler:", data["errors"][0]["message"])
                    # Falls seriesEvents nicht existiert, probieren wir es innerhalb von seriesState
                    return False
                else:
                    os.makedirs("data/raw", exist_ok=True)
                    with open("data/raw/real_events.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                    print("ERFOLG! Events in data/raw/real_events.json gespeichert.")
                    return True
            else:
                print(f"Server Fehler: {r.status_code}")
                return False
        except Exception as e:
            print(f"Verbindungsfehler: {e}")
            return False

if __name__ == "__main__":
    fetch_events_gql()
