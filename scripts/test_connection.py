import asyncio
import httpx
import os
from dotenv import load_dotenv

async def test():
    load_dotenv()
    api_key = os.getenv('GRID_API_KEY')
    series_id = '28'
    url = f'https://api-op.grid.gg/live-data-feed/v1/series/{series_id}/state'
    
    headers = {
        'x-api-key': api_key,
        'Accept': 'application/json'
    }
    
    print(f'--- Teste Verbindung zu GRID (Series {series_id}) ---')
    print(f'URL: {url}')
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            print(f'Status Code: {response.status_code}')
            if response.status_code == 200:
                print('Erfolg! Daten empfangen.')
                data = response.json()
                print(f"Match: {data.get('externalId', 'Unbekannt')}")
            else:
                print(f'Fehler-Details: {response.text[:500]}')
        except Exception as e:
            print(f'Verbindungsfehler: {e}')

if __name__ == "__main__":
    asyncio.run(test())

