import asyncio
import httpx
import os
from dotenv import load_dotenv

async def test_alt_url():
    load_dotenv()
    api_key = os.getenv('GRID_API_KEY')
    ids = ['28', '1'] # Teste ID 28 und 1
    
    headers = {
        'x-api-key': api_key,
        'Accept': 'application/json'
    }
    
    # Alte URL Struktur
    print("--- Teste Alternative GRID URL Struktur ---")
    async with httpx.AsyncClient(timeout=5.0) as client:
        for sid in ids:
            url = f'https://api.grid.gg/series/{sid}/state'
            try:
                response = await client.get(url, headers=headers)
                print(f'URL: {url}')
                print(f'ID {sid:3} | Status: {response.status_code}')
                if response.status_code == 200:
                    print('      -> ERFOLG!')
            except Exception as e:
                print(f'ID {sid:3} | Fehler: {e}')

if __name__ == "__main__":
    asyncio.run(test_alt_url())

