import httpx
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

def find_active_series():
    load_dotenv()
    api_key = os.getenv('GRID_API_KEY')
    if not api_key:
        print("Fehler: GRID_API_KEY nicht in .env gefunden.")
        return

    url = 'https://api-op.grid.gg/central-data/graphql'
    
    # Zeitfenster: Letzte 24 Stunden bis nächste 24 Stunden
    now = datetime.utcnow()
    start = (now - timedelta(hours=24)).isoformat() + 'Z'
    end = (now + timedelta(hours=24)).isoformat() + 'Z'

    # Wir nutzen String statt DateTime! basierend auf der Fehlermeldung
    query = """
    query GetRecentSeries($start: String!, $end: String!) {
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
            startTimeScheduled
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

    try:
        response = httpx.post(url, json={'query': query, 'variables': variables}, headers=headers, timeout=20.0)
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"GraphQL Fehler: {data['errors']}")
                return

            edges = data.get('data', {}).get('allSeries', {}).get('edges', [])
            if not edges:
                print("Keine Serien im Zeitfenster gefunden.")
                return

            print(f"\nGefundene Serien ({len(edges)}):")
            for edge in edges:
                n = edge['node']
                sid = n['id']
                tourney = n.get('tournament', {}).get('nameShortened', 'N/A')
                title = n.get('title', {}).get('nameShortened', 'N/A')
                time = n.get('startTimeScheduled', 'N/A')
                print(f"ID: {sid} | {time} | {tourney} | {title}")
        else:
            print(f"HTTP Fehler {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Verbindungsfehler: {e}")

if __name__ == "__main__":
    find_active_series()
