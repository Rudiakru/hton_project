import httpx
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
api_key = os.getenv('GRID_API_KEY')

url = 'https://api.grid.gg/central-data/graphql'

now = datetime.utcnow()
start = (now - timedelta(days=2)).isoformat() + 'Z'
end = (now + timedelta(days=2)).isoformat() + 'Z'

query = """
query GetRecentSeries($start: DateTime!, $end: DateTime!) {
  allSeries(
    filter: {
      startTimeScheduled: {
        gte: $start
        lte: $end
      }
    }
    orderBy: StartTimeScheduled
  ) {
    edges {
      node {
        id
        title {
          nameShortened
        }
        tournament {
          nameShortened
        }
      }
    }
  }
}
"""

variables = {
    'start': start,
    'end': end
}

headers = {
    'x-api-key': api_key,
    'Content-Type': 'application/json'
}

print(f"Suche nach Serien zwischen {start} und {end}...")

try:
    response = httpx.post(url, json={'query': query, 'variables': variables}, headers=headers, timeout=30.0)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if 'errors' in data:
            print(f"GraphQL Fehler: {json.dumps(data['errors'], indent=2)}")
        
        series_edges = data.get('data', {}).get('allSeries', {}).get('edges', [])
        if not series_edges:
            print("Keine aktuellen Serien gefunden.")
        else:
            print(f"Gefundene Serien ({len(series_edges)}):")
            for edge in series_edges:
                n = edge['node']
                print(f"ID: {n['id']} | {n.get('tournament', {}).get('nameShortened')} | {n.get('title', {}).get('nameShortened')}")
    else:
        print(f"Fehler: {response.text}")
except Exception as e:
    print(f"Fehler: {e}")

