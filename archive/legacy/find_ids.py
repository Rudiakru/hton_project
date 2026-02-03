import httpx, os, json
from dotenv import load_dotenv
load_dotenv()

def find():
    api_key = os.getenv("GRID_API_KEY")
    url = "https://api-op.grid.gg/central-data/graphql"
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    
    # Wir fragen nach ALLEN Serien, die dein Key darf, ohne Turnier-Filter
    query = "{ allSeries(limit: 10) { edges { node { id tournament { name } teams { baseInfo { name } } } } } }"
    
    with httpx.Client() as client:
        try:
            r = client.post(url, headers=headers, json={"query": query})
            if r.status_code == 200:
                data = r.json()
                series = data.get("data", {}).get("allSeries", {}).get("edges", [])
                if not series:
                    print("Keine Serien gefunden. Key hat evtl. keine Scopes fuer Central Data.")
                for s in series:
                    node = s["node"]
                    t_name = node.get('tournament', {}).get('name', 'N/A')
                    teams = ' vs '.join([t.get('baseInfo', {}).get('name', 'N/A') for t in node.get('teams', [])])
                    print(f"ID: {node['id']} | {t_name} | {teams}")
            else:
                print(f"Fehler {r.status_code}: {r.text}")
        except Exception as e:
            print(f"Verbindungsfehler: {e}")

if __name__ == "__main__":
    find()

